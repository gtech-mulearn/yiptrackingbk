# Employee Manager API

> NB : Read About Solution Section for clarification about the solution

Designing and developing an efficient employee management system is crucial for businesses to streamline their human resources processes. The challenge is to create a web application with REST API endpoints that allow CRUD (Create, Read, Update, Delete) operations on employee and department data. Additionally, the system should include functionality to assign employees to departments and promote eligible employees to manager positions based on experience criteria.

> API Hosted on vercel : <a href="https://employee-manager-silk.vercel.app/">https://employee-manager-silk.vercel.app/</a>

## About the solution

> All demanding solutions for the problem statment 2 of GTA:Sandshore is implemented in this API

- In our product anyone can create an account. (Employee, Admin, CEO, Managers etc.)
- An admin or CEO of an organization can create an Organization and add their departments, and employees for each department. 
- The admin of an organization can also add a registerd user in this platform as an employee, or he can create an anonymous one.
- Admin can change or add an employee as a manager of a department.
- Admin can increase or decrease the salary of each employee depending on the year of experience
- Admin can change the department of an employee
- Here the **Admin means** the one who created the Organization.
- They have options to update any relevent details they want.

### Technical Explanation

- We use Django and rest framework for implementing the solution.
- We use **JWT Bearer** token for authenticating a user.
- all api endpoints are included in te `/api` folder
- all models in : `/api/models.py`
- API Tested using **Hoppscotch**

## API End points

> &lt;endpoint> - &lt;method>

- `/api/auth/register/` - POST
- `/api/auth/token/` - POST
- `/api/auth/verify/` - GET
- `/api/organization/` GET
- `/api/organization/create/` - POST
- `/api/organization/update/` - PUT
- `/api/organization/delete/` - DELETE
- `/api/organization/<org_id>/department/` - GET
- `/api/organization/<org_id>/department/create/` - POST
- `/api/organization/<org_id>/department/update/` - PUT
- `/api/organization/<org_id>/department/delete/` - DELETE
- `/api/organization/<org_id>/department/<dep_id>/employee/` - GET
- `/api/organization/<org_id>/department/<dep_id>/employee/create/` - POST
- `/api/organization/<org_id>/departments/<dep_id>/employee/update/` - PUT
- `/api/organization/<org_id>/departments/<dep_id>/employee/delete/` - DELETE

> For any doubts or queries, dont hesitate to contact.
