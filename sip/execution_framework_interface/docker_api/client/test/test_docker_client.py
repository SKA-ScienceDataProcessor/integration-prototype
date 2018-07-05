from docker_client import DockerClient

dc = DockerClient()


# Simple docker compose test
# filename = "compose-file/docker-compose.yml"
# dc.create_service(filename)



print("Create Service")
#filename = "compose-file/docker-compose.visibility.yml"
filename = "compose-file/vis_receive_example.yml"
dc.create_services(filename)
print("")

# Test create volume
# print("Create Volume")
# dc.create_volume('test')
# print("")

# Get volume
print("Get Details of Docker Volume")
volume = dc.get_volume_details('test')
print(volume)
print("")


# kwargs = {'first_name': 'Bobby', 'last_name': 'Smith'}
# dc.print_keyword_args(**kwargs)

# # Delete service
# # #dc.delete_service("config_database")
# #
# #
# # # Service list
# #
# # dc.get_service_list()
# #
# # # Get service details
# #
# # print(dc.get_service_details("config_database"))
# #
# # # Delete all the services
# # #dc.delete_all_services()
# #
# # # Get node list
# # node_list = dc.get_node_list()
# # for nodes_id in node_list:
# #     print(nodes_id)
# #
# # # Get a node
# #
# # print(dc.get_node_details('nrwa2fzkn5gaczmxfuovlwfuv'))