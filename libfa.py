import os, json


def get_stage_identifier(verbose=False):
    if os.path.exists('config/stage_identifier'):
        with open('config/stage_identifier', 'r') as fin:
            if verbose:
                print('[LOAD] `{}`'.format(os.path.abspath('config/stage_identifier')))
            return fin.readline().strip()

    print('[ERROR] No stage identifier found (expected: `{}`)'.format(os.path.join(os.path.abspath('.'), 'config/stage_identifier')))

    return None


def get_stage_configuration(stage_identifier, verbose=True):
    assert stage_identifier is not None
    stage_identifier = str(stage_identifier)

    if verbose:
        print('[INFORMATION] Use stage identifier \'{}\''.format(stage_identifier))

    assert len(stage_identifier) > 0

    if os.path.exists('config/stage_configurations.json'):
        with open('config/stage_configurations.json', 'r', encoding='UTF-8') as fin:
            stage_configurations = json.loads(fin.read())

            for stage_configuration in stage_configurations:
                if stage_configuration['stage'] == stage_identifier:
                    if verbose:
                        print('[INFORMATION] Load stage configuration \'{}\''.format(stage_configuration))

                    return stage_configuration

        print('[ERROR] No \'{}\' stage configuration found'.format(stage_identifier))

    print('[ERROR] No stage configurations found (expected: `{}`)'.format(os.path.join(os.path.abspath('.'), 'config/stage_configurations.json')))

    return None


def get_stage_values(key):
    site_identifier = get_stage_identifier(verbose=False)
    stage_configuration = get_stage_configuration(site_identifier, verbose=False)

    if key in stage_configuration:
        return stage_configuration[key]

    print('[ERROR] `get_stage_values()` | No `key`=\'{}\' found'.format(key))

    return None


# def find_stage_configuration(stage_identifier):
#     stage_configurations_file_path = os.path.join('./config', 'stage_configurations.json')
#
#     with open(stage_configurations_file_path) as fin:
#         stage_configurations = json.loads(fin.read())
#
#     for stage_configuration in stage_configurations:
#         if stage_identifier == stage_configuration['stage']:
#             return stage_configuration


def update_stage_configuration(stage_configuration):
    stage_identifier = stage_configuration['stage']

    stage_configurations_file_path = os.path.join('./config', 'stage_configurations.json')

    with open(stage_configurations_file_path) as fin:
        stage_configurations = json.loads(fin.read())

    stage_configurations = [item for item in stage_configurations if item['stage'] != stage_identifier]  # remove target stage

    stage_configurations.append(stage_configuration)  # update stage

    with open(stage_configurations_file_path, 'w') as fout:
        json.dump(stage_configurations, fout, indent=4, sort_keys=True)

    return stage_configurations
