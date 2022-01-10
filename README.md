# TaskTracker
Python Flask web app to manage user specific to-do lists for organizations

IDE: VS Code, DB: SQLite, shell: PowerShell, Venv control: Miniconda, deployment: AWS/Docker

Any site visitor can create user account.
Users create organizations. User who creates organization is automatically an organization admin.
Users may join/leave any organization.
Organization creator may not leave organization.
Pending tasks assigned to user are unassigned when user leaves organization.
Any organization admin can give admin access to other users within the organization.
Users may be members of any number of organizations and have admin rights specific to individual organizations.
Any member of an organization can create to-do tasks specific to that organization.
Users may assign themselves to any task that they created.
Organization admins can assign any organization task to users within the organization.
Users may see detailed task info for any task they've created or been assigned.
Organization admins can see detailed task info for any tasks within the organization.
Organization admins can clear completed tasks from the organizaion task record.

![image](https://user-images.githubusercontent.com/72046035/146285601-a82decf4-2556-45a4-be8d-73b0a9e554ff.png)
