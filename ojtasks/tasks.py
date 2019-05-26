from actips.celery import app
from core import models as m

from ojadapter.adapter import ALL_ADAPTERS


@app.task
def pull_problems_all():
    results = []
    for site in m.OnlineJudgeSite.objects.all():
        result = pull_problems_oj.delay(site.code)
        results.append(result.id)
    return results


@app.task
def pull_problems_oj(oj_code):
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
            print(pid)
            result.get()
            results.append(pid)
    return results


@app.task
def pull_problem_oj(oj_code, problem_id, contest_id=''):
    site = m.OnlineJudgeSite.objects.filter(code=oj_code).first()
    if not site:
        return None
    problem = site.download_problem(problem_id, contest_id)
    return problem.id
