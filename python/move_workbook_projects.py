####
# This script contains functions that demonstrate how to move
# a workbook from one project to another.
#
# To run the script, you must have installed Python 2.7.9 or later,
# plus the 'requests' library:
#   http://docs.python-requests.org/en/latest/
#
# The script takes in the server address and username as arguments,
# where the server address has no trailing slash (e.g. http://localhost).
# Run the script in terminal by entering:
#   python move_workbook_projects.py <server_address> <username>
#
# When running the script, it will prompt for the following:
# 'Name of workbook to move': Enter name of workbook to move
# 'Destination project':      Enter name of project to move workbook into
# 'Password':                 Enter password for the user to log in as.
####

from credentials import SERVER, USERNAME, PASSWORD, SITENAME
from version import VERSION
import requests # Contains methods used to make HTTP requests
import xml.etree.ElementTree as ET # Contains methods used to build and parse XML

import getpass
from rest_api_utils import _check_status, ApiCallError, UserDefinedFieldError, _encode_for_display, sign_in, sign_out

from rest_api_common import get_project_id

# If using python version 3.x, 'raw_input()' is changed to 'input()'
if sys.version[0] == '3': raw_input=input



def move_workbook(server, auth_token, site_id, workbook_id, project_id):
    """
    Moves the specified workbook to another project.

    'server'        specified server address
    'auth_token'    authentication token that grants user access to API calls
    'site_id'       ID of the site that the user is signed into
    'workbook_id'   ID of the workbook to move
    'project_id'    ID of the project to move workbook into
    """
    url = server + "/api/{0}/sites/{1}/workbooks/{2}".format(VERSION, site_id, workbook_id)
    # Build the request to move workbook
    xml_request = ET.Element('tsRequest')
    workbook_element = ET.SubElement(xml_request, 'workbook')
    ET.SubElement(workbook_element, 'project', id=project_id)
    xml_request = ET.tostring(xml_request)

    server_response = requests.put(url, data=xml_request, headers={'x-tableau-auth': auth_token})
    _check_status(server_response, 200)


def main():
    ##### STEP 0: INITIALIZATION #####

    server = SERVER
    username = USERNAME
    password = PASSWORD
    site_id = SITENAME
    workbook_name = raw_input("\nName of workbook to move: ")
    dest_project = raw_input("\nDestination project: ")

    print("\n*Moving '{0}' workbook to '{1}' project as {2}*".format(workbook_name, dest_project, username))
    password = getpass.getpass("Password: ")

    ##### STEP 1: Sign in #####
    print("\n1. Signing in as " + username)
    auth_token, site_id, user_id = sign_in(server, username, password)

    ##### STEP 2: Find new project id #####
    print("\n2. Finding project id of '{0}'".format(dest_project))
    dest_project_id = get_project_id(server, auth_token, site_id, dest_project)

    ##### STEP 3: Find workbook id #####
    print("\n3. Finding workbook id of '{0}'".format(workbook_name))
    source_project_id, workbook_id = get_workbook_id(server, auth_token, user_id, site_id, workbook_name)

    # Check if the workbook is already in the desired project
    if source_project_id == dest_project_id:
        error = "Workbook already in destination project"
        raise UserDefinedFieldError(error)

    ##### STEP 4: Move workbook #####
    print("\n4. Moving workbook to '{0}'".format(dest_project))
    move_workbook(server, auth_token, site_id, workbook_id, dest_project_id)

    ##### STEP 5: Sign out #####
    print("\n5. Signing out and invalidating the authentication token")
    sign_out(server, auth_token)


if __name__ == "__main__":
    main()
