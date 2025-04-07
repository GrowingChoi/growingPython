CREATE TABLE emp(
    emp_id 	  INT PRIMARY KEY,
    emp_name  VARCHAR(20) NOT NULL,
    job_id 	  VARCHAR(30),
    mgr_id 	  INT,
    hire_date DATE NOT NULL,
    salary 	  DECIMAL(7,2) NOT NULL,
    comm_pct  DECIMAL(2,2),
    dept_id   INT,
    CONSTRAINT fk_emp_dept FOREIGN KEY(dept_id) REFERENCES dept(dept_id) ON DELETE SET NULL,
    CONSTRAINT fk_emp_job FOREIGN KEY(job_id) REFERENCES job(job_id) ON DELETE SET NULL,
    CONSTRAINT fk_emp_mgr FOREIGN KEY(mgr_id) REFERENCES emp(emp_id) ON DELETE SET NULL
);