# #!/usr/bin/env python3
#
# from rofm.classes.util.configuration import Config, Section, Subsection
#
#
# # noinspection PyTypeChecker
# def config_is_complete_and_concise():
#     Config("../config.ini")
#     config_specified_sections = list(Config.config.keys())
#     config_specified_subsections = [k for s in list(Config.config.values()) for k in s.keys()]
#
#     # Ignore "DEFAULT" section in config
#     default = {"DEFAULT"}
#     config_specified_sections = set(config_specified_sections).difference(default)
#     config_specified_subsections = set(config_specified_subsections).difference(default)
#
#     enumerated_sections = set(s.name for s in Section).difference(default)
#     enumerated_subsections = set(s.name for s in Subsection).difference(default)
#
#     sections_missing_enum = config_specified_sections.difference(enumerated_sections)
#     subsections_missing_enum = config_specified_subsections.difference(enumerated_subsections)
#
#     sections_missing_config = enumerated_sections.difference(config_specified_sections)
#     subsections_missing_config = enumerated_subsections.difference(config_specified_subsections)
#
#     assert not sections_missing_config, "sections_missing_config: {}".format(sections_missing_config)
#     assert not sections_missing_enum, "sections_missing_enum: {}".format(sections_missing_enum)
#     assert not subsections_missing_config, "subsections_missing_config: {}".format(subsections_missing_config)
#     assert not subsections_missing_enum, "subsections_missing_enum: {}".format(subsections_missing_enum)
#
#
# if __name__ == '__main__':
#     config_is_complete_and_concise()
#     print("Passed.")