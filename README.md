## Resource Assignment Problem
### Data
The list $R$ contains the names of the user-entered resources

The list $J$ contains the names of different job types

$r \in R$: index and set of resources. The resource $r$ belongs to the set of resources $R$.

$j \in J$: index and set of job types. The job type $j$ belongs to the set of job types $J$.

### Parameters
$max\_jobs \in \mathbb{R^{+}}$: max number of jobs that can be undertaken by a resource.

### Decision variable
$x_{r,j} \in \mathbb{R^{+}}$: number of jobs of type $j$ performed by resource $r$ 

### Constraints
$\sum_{j \in J}x_{r,j} \leq max\_jobs$ for each resource $\forall$ $r \in R$



### Objective
- $\sum_{r \in R}\sum_{j \in J}x_{r,j}$: **Maximize** sum of jobs performed (Higher priority)
- $\sum_{r \choose 2}(\left\lvert\sum_{j \in J}x_{r1,j} - \sum_{j \in J}x_{r2,j} \right\rvert)$: **Minimize**, make the jobs distribution equitable across  (Lower priority)
