from actips.celery import app
from core import models as m

from ojadapter.adapter import ALL_ADAPTERS


@app.task
def pull_problems_all():
    """ 抓取所有OJ所有的题目
    :return:
    """
    results = []
    for site in m.OnlineJudgeSite.objects.all():
        result = pull_problems_oj.delay(site.code)
        results.append(result.id)
    return results


@app.task
def pull_problems_oj(oj_code):
    """ 抓取某个OJ所有的题目
    :param oj_code:
    :return:
    """
    if oj_code not in ALL_ADAPTERS or \
            not m.OnlineJudgeSite.objects.filter(code=oj_code).exists():
        return False
    adapter = ALL_ADAPTERS[oj_code]
    results = []
    for pid in adapter.get_all_problem_numbers():
        problem = m.OnlineJudgeProblem.objects.filter(
            site__code=oj_code, num=pid).first()
        # 如果题目没有抓取过才抓取
        if not problem or not problem.is_synced:
            result = pull_problem_oj.delay(oj_code, pid)
            # print(pid)
            # result.get()
            results.append(pid)
    return results


@app.task
def pull_problem_oj(oj_code, problem_id, contest_id=''):
    """ 抓取某个OJ指定编号的题目
    :param oj_code:
    :param problem_id:
    :param contest_id:
    :return:
    """
    site = m.OnlineJudgeSite.objects.filter(code=oj_code).first()
    if not site:
        return None
    problem = site.download_problem(problem_id, contest_id)
    return problem.id


@app.task
def pull_user_submissions_oj(oj_code, user_id):
    """ 抓取某个用户在指定OJ上的提交记录 """
    site = m.OnlineJudgeSite.objects.filter(code=oj_code).first()
    if not site:
        return None
    profile = site.user_profiles.filter(user_id=user_id).first()
    if not profile:
        return
    profile.validate()
    profile.download_submissions()
    # submissions = site.


@app.task
def submit_online_judge_problem(problem_id, user_id, language_id, code, contest_id=None, use_platform_account=False):
    problem = m.OnlineJudgeProblem.objects.get(id=problem_id)
    user = m.User.objects.get(id=user_id)
    profile = m.OnlineJudgeUserProfile.objects.filter(user=user, site=problem.site).first()
    adapter = problem.site.get_adapter()
    if profile and not use_platform_account:
        profile.validate()
        ctx = profile.get_context()
    else:
        ctx = adapter.get_platform_user_context()
    submission = adapter.submit_problem(ctx, problem.num, language_id, code, contest_id)
    s = m.OnlineJudgeSubmission.make(submission, problem.site, user)
    return s.id
