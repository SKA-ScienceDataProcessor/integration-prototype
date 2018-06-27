# -*- coding: utf-8 -*-

"processing_block":
{
    "resource_requirements":
    {
        buffer: "10TB"
        total_nodes: 5
    },
    "workflow_template": {},
    "workflow_config":
    [
        {
            "type": "init_buffers",
            "ee_type": "docker_swarm",
            "config": {

            }
        },

        {
            "type": "vis_send",
            "ee_type": "docker_swarm",
            "config":
            {
                "num_senders": 5,
                "compose_template": "path/to/compose_template.yml.j2",
                "config_template": "/path/to/config.json.j2"
                "receiver_nodes": ['ip1', 'ip2']
            }
        },

        {
            "type": "vis_recv",
            "ee_type": "docker_swarm",
            "config": {
                "compose_template": {
                    "path": "path/to/compose_template.yml.j2",
                    "num_receivers": 5
                },
                "config": {
                    "path": "/path/to/config.json",
                }
            }
        },
    ]


}



def load_template(filename):
    """."""
    num_recievers = 3
    with open(filename, 'r')
