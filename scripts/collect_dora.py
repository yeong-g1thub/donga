import json
import os
import statistics
from datetime import datetime, timedelta, timezone
from urllib.request import Request, urlopen


TOKEN = os.environ["GITHUB_TOKEN"]
REPOSITORY = os.environ["GITHUB_REPOSITORY"]

API = "https://api.github.com"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2026-03-10"
}


def github_get(path, params=""):
    url = API + path

    if params:
        url += "?" + params

    request = Request(
        url,
        headers=HEADERS
    )

    with urlopen(request) as response:
        return json.loads(response.read())


def parse_time(value):
    return datetime.fromisoformat(
        value.replace("Z", "+00:00")
    )


def get_workflow_runs():

    owner, repo = REPOSITORY.split("/")

    path = f"/repos/{owner}/{repo}/actions/workflows/deploy.yml/runs"

    data = github_get(
        path,
        "branch=main&per_page=100"
    )

    return data["workflow_runs"]


def get_commit(sha):

    owner, repo = REPOSITORY.split("/")

    return github_get(
        f"/repos/{owner}/{repo}/commits/{sha}"
    )


def main():

    now = datetime.now(timezone.utc)

    start = now - timedelta(days=7)

    runs = get_workflow_runs()

    deployments = []

    lead_times = []

    failed_deployments = []

    recovery_times = []

    for run in runs:

        if run["event"] not in [
            "push",
            "workflow_dispatch"
        ]:
            continue

        created = parse_time(run["created_at"])

        if created < start:
            continue

        sha = run["head_sha"]

        conclusion = run["conclusion"]

        deployment_time = parse_time(
            run["updated_at"]
        )

        commit = get_commit(sha)

        commit_time = parse_time(
            commit["commit"]["committer"]["date"]
        )

        lead_time = (
            deployment_time - commit_time
        ).total_seconds() / 60

        # 성공한 Production deployment만 DORA deployment로
        if conclusion == "success":

            lead_times.append(lead_time)

            deployments.append({
                "date": deployment_time.date().isoformat(),
                "sha": sha[:7],
                "status": "success",
                "lead_time_minutes": round(
                    lead_time,
                    2
                )
            })

        elif conclusion == "failure":

            failed_deployments.append({
                "date": deployment_time.date().isoformat(),
                "sha": sha[:7],
                "status": "failure"
            })

  
    # 실패한 production deployment 이후 다음 성공 deployment까지의 시간을 recovery time으로

    successful_times = []

    for deployment in deployments:
        successful_times.append(
            datetime.fromisoformat(
                deployment["date"]
            ).replace(tzinfo=timezone.utc)
        )

    # 실패 수와 성공 수를 기준으로 Change Failure Rate 계산
    total_deployments = (
        len(deployments)
        + len(failed_deployments)
    )

    change_failure_rate = (
        len(failed_deployments)
        / total_deployments
        if total_deployments > 0
        else 0
    )

    deployment_frequency = (
        len(deployments)
    )

    average_lead_time = (
        statistics.mean(lead_times)
        if lead_times
        else 0
    )

    average_mttr = (
        statistics.mean(recovery_times)
        if recovery_times
        else 0
    )

    result = {

        "generated_at":
            now.isoformat(),

        "period": {
            "start": start.isoformat(),
            "end": now.isoformat()
        },

        "metrics": {

            "lead_time_minutes":
                round(
                    average_lead_time,
                    2
                ),

            "deployment_frequency":
                deployment_frequency,

            "mttr_minutes":
                round(
                    average_mttr,
                    2
                ),

            "change_failure_rate":
                round(
                    change_failure_rate,
                    4
                )
        },

        "deployments":
            deployments,

        "failed_deployments":
            failed_deployments
    }

    os.makedirs(
        "data",
        exist_ok=True
    )

    with open(
        "data/dora-metrics.json",
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            result,
            file,
            indent=2,
            ensure_ascii=False
        )

    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False
        )
    )


if __name__ == "__main__":
    main()
