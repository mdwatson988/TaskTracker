# TaskTracker
Python Flask web app to manage user specific to-do lists for organizations

IDE: VS Code, DB: SQLite, shell: PowerShell, Venv control: Miniconda, deployment: AWS/Docker

Any site visitor can create user account.
Users create organizations. User who creates organization is automatically an organization admin.
Users may join any already created organization.
Any organization admin can give admin access to other users within the organization.
Users may be members of any number of organizations and have admin rights specific to individual organizations.
Any member of an organization can create to-do tasks specific to that organization.
Users may assign themselves to any task that they created.
Organization admins can assign any organization task to users within the organization.
Users may see detailed task info for any task they've been assigned.
Organization admins can see detailed task info for any tasks within the organization.

![image](https://user-images.githubusercontent.com/72046035/146062712-6714f325-b9c5-4e97-8c28-96a11bd1096b.png)
