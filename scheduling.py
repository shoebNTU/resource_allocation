import string
from itertools import combinations

import gurobipy as gp
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Resource Allocation", initial_sidebar_state="expanded", layout="wide"
)
st.sidebar.title("Scheduling inputs")

alphabet_upper = list(string.ascii_uppercase)
alphabet_lower = list(string.ascii_lowercase)

# Enter number of resources
no_of_resources = st.sidebar.number_input(
    "Please enter number of resources", min_value=1, max_value=26
)

# Enter number of job types
no_of_job_types = st.sidebar.number_input(
    "Please enter number of job types", min_value=1, max_value=26
)

# max number of resources
max_days_resource = st.sidebar.number_input(
    "Please enter maximum number of jobs a resource can perform", min_value=1, value=1
)

# Enter names of resources
c1, c2, c3, c4 = st.columns(4)

resources = []
with c1:
    st.header("Resources")
    for i in range(no_of_resources):
        resource_name = st.text_input(
            "Please enter resource name", key=i, value=alphabet_upper[i]
        )
        if resource_name == "" or resource_name in resources:
            st.error("Resource names cannot be empty or duplicate")
        else:
            resources.append(resource_name)

# Enter job types
job_types = []
with c2:
    st.header("Job types")
    for i in range(no_of_job_types):
        job_name = st.text_input(
            "Please enter job type", key="job" + str(i), value=alphabet_lower[i]
        )
        if job_name == "" or job_name in job_types:
            st.error("Resource names cannot be empty or duplicate")
        else:
            job_types.append(job_name)

if len(job_types) == no_of_job_types and len(resources) == no_of_resources:
    resource_to_jobs = []
    resource_job_mapping = {}
    # Resources to job types mapping
    with c3:
        st.header("Mapping")
        for i in range(no_of_resources):
            resource_to_job = st.multiselect(
                f"Eligible jobs for resource - {resources[i]}",
                job_types,
                key="job-resource" + str(i),
            )
            resource_job_mapping[resources[i]] = resource_to_job
            resource_to_jobs.append(resource_to_job)

    with c4:
        job_days = {}
        st.header("No. of jobs")
        for i in range(no_of_job_types):
            no_of_jobs = st.number_input(
                f"No. of jobs for job type - {job_types[i]}",
                min_value=0,
                value=1,
                key="no_jobs" + str(i),
            )
            job_days[job_types[i]] = no_of_jobs

    # Optimize
    optimize = st.button("Optimize")
    if optimize:
        m = gp.Model("QD")
        x = m.addVars(resources, job_types, vtype=gp.GRB.INTEGER)
        resource_to_job = m.addConstrs(
            x[resource, job] == 0
            for resource in resources
            for job in job_types
            if job not in resource_job_mapping[resource]
        )
        resource_max = m.addConstrs(
            gp.quicksum(x[resource, job] for job in job_types) <= max_days_resource
            for resource in resources
        )
        job_completion = m.addConstrs(
            gp.quicksum(x[resource, job] for resource in resources) <= job_days[job]
            for job in job_types
        )
        # equal_distribution_cons = m.addConstrs(gp.quicksum(x[resource,job] for job in job_types) >= equal_distribution for resource in resources)
        obj = gp.quicksum(
            -x[resource, job] for resource in resources for job in job_types
        )

        resource_days = m.addVars(resources, vtype=gp.GRB.INTEGER)
        m.addConstrs(
            (
                resource_days[resource]
                == gp.quicksum(x[resource, job] for job in job_types)
            )
            for resource in resources
        )
        res_comb = list(
            combinations(resources, 2)
        )  # combination of resources, clubbed two at a time!
        y = m.addVars(res_comb, vtype=gp.GRB.INTEGER, lb=-gp.GRB.INFINITY)
        z = m.addVars(res_comb, vtype=gp.GRB.INTEGER)
        m.addConstrs(
            (y[ij[0], ij[1]] == (resource_days[ij[0]] - resource_days[ij[1]]))
            for ij in res_comb
        )
        m.addConstrs(z[ij[0], ij[1]] == gp.abs_(y[ij[0], ij[1]]) for ij in res_comb)

        m.setObjectiveN(obj, index=0, priority=2)
        m.setObjectiveN(z.sum(), index=1, priority=1)
        m.optimize()

        solution = np.reshape(
            m.getAttr("X", x.values()), (len(resources), len(job_types))
        )
        solution = np.hstack((solution, solution.sum(axis=1).reshape(-1, 1)))
        solution_df = pd.DataFrame(solution, columns=job_types + ["Total"], index=resources)
        st.write(solution_df)
        st.info(f"Total no. of user-entered jobs: {sum(job_days.values())}")
        st.info(f"Total no. of scheduled jobs: {int(solution_df['Total'].sum())}")
