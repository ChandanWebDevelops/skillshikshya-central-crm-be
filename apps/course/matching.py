import logging
import re

import requests

from django.conf import settings

from apps.course.models import Course, CourseCategory

logger = logging.getLogger(__name__)

# Public Skill Shikshya course catalog API
PUBLIC_COURSE_API_URL = getattr(
    settings, 'PUBLIC_COURSE_API_URL', 'https://base.skillshikshya.com/api/course/'
)

STOPWORDS = {
    'course', 'courses', 'diploma', 'training', 'program', 'programme',
    'masterclass', 'master', 'class', 'job', 'ready', 'in', 'nepal',
    'with', 'and', 'the', 'for', 'of', 'to', 'on', 'online', 'professional',
    'complete', 'basic', 'advanced', 'foundation', 'bootcamp',
    'skill', 'shikshya', 'trial', 'free', 'ne', 'an', 'ai',
    'integrated', 'day', 'days', 'full', 'stack', 'web', 'development',
    'designing', 'design', 'graphics', 'graphic',
}

MATCH_THRESHOLD = 0.6

# In-process cache for the public catalog
_CACHE = {}


def _normalize(name):
    text = (name or '').lower()
    text = re.sub(r'[^a-z0-9 ]+', ' ', text)
    tokens = {t for t in text.split() if t and t not in STOPWORDS}
    return tokens


def _match_score(query_tokens, candidate_tokens):
    if not query_tokens or not candidate_tokens:
        return 0.0
    intersection = query_tokens & candidate_tokens
    if not intersection:
        return 0.0
    completeness = len(intersection) / len(query_tokens)
    union = query_tokens | candidate_tokens
    coverage = len(intersection) / len(union)
    return 0.7 * completeness + 0.3 * coverage


def _fetch_public_courses():
    cached = _CACHE.get('public')
    if cached is not None:
        return cached or None

    results = []
    url = PUBLIC_COURSE_API_URL
    try:
        while url:
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            results.extend(data.get('results', []) or [])
            url = data.get('next')
    except Exception as exc:
        logger.warning('Public course API unavailable (%s); falling back to local table', exc)
        _CACHE['public'] = None
        return None

    _CACHE['public'] = results
    return results


def _upsert_from_public(item, requested_name, full_amount):
    title = (item.get('title') or requested_name).strip()
    if not title:
        return None, False

    public_amount = item.get('amount')
    if public_amount is None or public_amount == '':
        amount = full_amount if full_amount is not None else '0.00'
    else:
        amount = public_amount

    course, created = Course.objects.get_or_create(
        name=title,
        defaults={'full_amount': amount},
    )
    if not created and course.full_amount is None:
        course.full_amount = amount
        course.save(update_fields=['full_amount'])

    for cat in item.get('categories') or []:
        cat_name = cat.get('name') if isinstance(cat, dict) else cat
        if not cat_name:
            continue
        category, _ = CourseCategory.objects.get_or_create(name=str(cat_name).strip())
        course.categories.add(category)

    return course, created


def match_or_create_course(raw_name, full_amount=None):
    """
    Resolve a plain-text inbound course name to a Course.

    Strategy:
      1. Match against the public SkillShikshya catalog by normalized tokens.
         On a hit, upsert the Course using the public amount (or 0.00) and
         attach its categories.
      2. If the public API is unavailable, fall back to matching against the
         local CRM course table.
      3. If still nothing matches, create a new Course with amount 0.00.
    """
    name = (raw_name or '').strip()
    if not name:
        return None, False

    query_tokens = _normalize(name)

    # 1. Public catalog match (preferred)
    public = _fetch_public_courses()
    if public is not None:
        best = None
        best_score = 0.0
        for item in public:
            title = item.get('title') or ''
            candidate_tokens = _normalize(title)
            score = _match_score(query_tokens, candidate_tokens)
            if score > best_score:
                best_score = score
                best = item
        if best and best_score >= MATCH_THRESHOLD:
            return _upsert_from_public(best, name, full_amount)

    # 2. Fallback: local CRM course table
    local_best = None
    local_score = 0.0
    for course in Course.objects.all():
        candidate_tokens = _normalize(course.name)
        score = _match_score(query_tokens, candidate_tokens)
        if score > local_score:
            local_score = score
            local_best = course
    if local_best and local_score >= MATCH_THRESHOLD:
        return local_best, False

    # 3. Create a new unmatched course (amount 0.00)
    course = Course.objects.create(name=name)
    return course, True