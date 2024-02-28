import frappe
import json
import subprocess
import os


@frappe.whitelist()
def create_site():
    site_name = "aaa"

    query = """
        SELECT name, site_name, site_status, site_job_type 
        FROM `tabSite Creation Details` 
        WHERE site_name = %s 
            AND (site_status = 'Live' OR site_job_type = 'Create')
           
    """

    try:
        site_exists = frappe.db.sql(query, (site_name,), as_dict=True)
        if site_exists:
            # [site_job_name,site_job_status]=create_new_site(site_name, password)
            # return Response({'message': 'Site creation process initiated successfully','site_job_name':site_job_name,'site_job_status':site_job_status}, status=status.HTTP_200_OK)
            return "Error"
        else:
            # return Response({'message': 'Site already exist in bench.','site_job_name':'','site_job_status':''}, status=status.HTTP_200_OK)
            return "Create New site"
    except Exception as e:
        # raise e
        print(e)
        # return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return "error"


# CREATE DOCKER IMAGE API
@frappe.whitelist(allow_guest=True)
def create_docker_image():
    # DEFAULT ARGUMENTS
    repository_name = "karanwebisoft/uctest:1.0.0"
    docker_username = "karanwebisoft"
    docker_password = "dckr_pat_eYQUrthdbh3Zd75oCYybYvzh6sY"

    # PATHS OF THE REQUIRED DIRS
    base_dir = os.path.dirname(os.path.abspath(__file__))
    apps_json_file_path = os.path.join(base_dir, "docker_files/apps.json")
    container_file_path = os.path.join(base_dir, "docker_files/Containerfile")
    entrypoint_file_path = os.path.join(base_dir, "docker_files/nginx-entrypoint.sh")
    template_file_path = os.path.join(base_dir, "docker_files/nginx-template.conf")

    # DEFINE ALL THE FUNCTIONS

    # FUNCTION TO CLONE FILES
    def CloneFiles(old_path, new_path):
        # OPEN AND READ THE OLD FILE
        with open(old_path, "r") as original_file:
            content = original_file.read()

        # WRITE IN NEW FILE
        with open(new_path, "w") as new_file:
            new_file.write(content)

        print(f"File cloned from {old_path} to {new_path}")

    # FUNCTION TO CONVERT BASE64
    def ConvertToBASE64(input_file_path, output_file_path):
        try:
            base64_command = (
                f"export {output_file_path}=$(base64 -w 0 {input_file_path})"
            )

            result = subprocess.run(
                base64_command,
                capture_output=True,
                shell=True,
                check=True,
                text=True,
            )

            if result.stdout:
                print(result.stdout)

            if result.stderr:
                print(result.stderr)

            print("File Has Been Successfully Converted to BASE64")

        except Exception as e:
            print(f"Error Converting File to BASE64 : {e}")

    # FUNCTION TO DOCKER BUILD
    def DockerBuild(base64_json_file, container_file_path, repo_name_and_tag):
        try:
            docker_build_command = f"""docker build \
                                        --build-arg=FRAPPE_PATH=https://github.com/frappe/frappe \
                                        --build-arg=FRAPPE_BRANCH=version-15 \
                                        --build-arg=PYTHON_VERSION=3.11.6 \
                                        --build-arg=NODE_VERSION=18.18.2 \
                                        --build-arg=APPS_JSON_BASE64=${base64_json_file} \
                                        --tag={repo_name_and_tag} \
                                        --file={container_file_path} ."""
            result = subprocess.run(
                docker_build_command,
                capture_output=True,
                text=True,
                shell=True,
            )

            if result.stdout:
                print(result.stdout)

            if result.stderr:
                print(result.stderr)

            print("The Docker File Has Been Created Successfully")

        except Exception as e:
            print(f"Error While Creating Docker image: {e}")

    # FUNCTION TO LOGIN TO DOCKER
    def LoginToDocker(username, password):
        try:

            docker_login_command = f"""docker logout
                                    docker login -u {username} -p {password}"""

            result = subprocess.run(
                docker_login_command,
                capture_output=True,
                text=True,
                shell=True,
            )

            if result.stdout:
                print(result.stdout)

            if result.stderr:
                print(result.stderr)

            print("Login Successful")

        except Exception as e:
            print(f"Error in Login : {e}")

    # FUNCTION TO PUSH IMAGE TO DOCKER
    def PushImageToDocker(repo_name_and_tag):
        try:
            docker_push_command = f"docker push {repo_name_and_tag}"

            result = subprocess.run(
                docker_push_command,
                capture_output=True,
                text=True,
                shell=True,
            )

            if result.stdout:
                print(result.stdout)

            if result.stderr:
                print(result.stderr)

            print("The Image is Successfully Pushed to Docker Repository")

        except Exception as e:
            print(f"There is an error while pushing to docker repository : {e}")

    # EXECUTE ALL THE FUNCTIONS WHICH ARE REQUIRED
    try:

        # CLONE THE ENTRYPOINT FILE AND ADD IT INTO THE SITES DIR
        CloneFiles(entrypoint_file_path, "nginx-entrypoint.sh")

        # CLONE THE TEMPLATE FILE AND ADD IT INTO THE SITES DIR
        CloneFiles(template_file_path, "nginx-template.conf")

        # CONVERT APPS.JSON FILE TO THE BASE64 FORMAT
        ConvertToBASE64(apps_json_file_path, "APPS_JSON_BASE64")

        # BUILD DOCKER IMAGE
        DockerBuild(
            "APPS_JSON_BASE64",
            container_file_path,
            repository_name,
        )

        # LOGIN NTO THE DOCKER ACCOUNT
        LoginToDocker(docker_username, docker_password)

        # PUSH IMAGE TO DOCKER HUB
        PushImageToDocker(repository_name)

        return "Image Has Been Successfully Created"

    except Exception as e:
        return f"Error Creating Image : {e}"
