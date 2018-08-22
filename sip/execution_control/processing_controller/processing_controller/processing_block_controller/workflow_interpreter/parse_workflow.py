# -*- coding: utf-8 -*-
"""."""
import json

# https://stackoverflow.com/questions/45129192/how-to-use-airflow-with-celery?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
# https://airflow.apache.org/configuration.html#scaling-out-with-celery


def follow_signal(workflow, signal, indent=4):
    """."""
    for process in workflow['processes']:
        # print('checking for {} in {} ({}) == {}'.
        #       format(signal, process['name'], process['ins'],
        #              (signal in process['ins'])))
        for _input in process['ins']:
            if signal in _input:
                print('{}<{}()> =={}=='.format(' '*indent, process['name'],
                                               process['ins']))
                for _output in process['outs']:
                    print('{}[{}]'.format(' '*(indent+4), _output))
                    follow_signal(workflow, _output, indent=indent+8)


def main():
    """."""
    workflow = json.load(open('workflow_01.json', 'r'))
    # print(json.dumps(workflow, indent=2))

    # Follow inputs

    for ii, _input in enumerate(workflow['ins']):
        print('[{}]'.format(_input))
        follow_signal(workflow, _input)
        # for process in workflow['processes']:
    #         if _input in process['ins']:
    #             print(process['name'], end=' -> ')
    #         for _output in process['outs']:
    #             print(_output, end='')
    #     print('')
    # for process in workflow['processes']:
    #     print(process['name'])


if __name__ == '__main__':
    main()
