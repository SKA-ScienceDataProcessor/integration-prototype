# db = masterClient()
# #
# name = ['execution_control', 'master_controller']
# field = 'SDP_state'
# value = db.get_state(name, field)
# print(value)

# # Get all state
# all = db.get_state_all(name)
# print(all)

# # Get all list
# service_list_name = ['execution_control', 'master_controller', 'service_list']
# list = db.get_service_list(service_list_name)
# for i in list:
#     print(i)
#
# # Get the length of service list
# length = db.get_service_list_length(service_list_name)
# print(length)
#
# print("Get the nth element from the list")
# element = db.get_service_from_list(service_list_name, 1)
# print(element)
# print("")
#
# print("Test return 0 if no nth element is found")
# element = db.get_service_from_list(service_list_name, 7)
# print(element)
# print("")
#
# print("Add element to the service list")
# # dict = {
# #           'name': 'sdp_services_test.data_queue_test',
# #           'enabled': 'False_test'
# #        }
# # db.add_service_to_list(service_list_name, dict)
# test_add_element = db.get_service_from_list(service_list_name, 0)
# print(test_add_element)
# print(test_add_element['name'])
# print(test_add_element['enabled'])
# print("")
#
# print("Converts a value from the database to a service path list")
# print("Updates the state of a service")
# element = db.get_service_from_list(service_list_name, 3)
# v_path = element['name']
# print(v_path)
# field = 'state'
# value = "stopped"
# db.update_service(v_path, field, value)
# print("")