import os
import re
from utils.file_utils import assemble_project_path, read_resource_file
from utils.json_utils import parse_semi_formatted_text

def _extract_keys_from_template(templage_path):
        template_path = assemble_project_path(templage_path)
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template file {template_path} does not exist")

        template = read_resource_file(template_path)

        # <$few_shots$> -> few_shots
        parse_input_keys = re.findall(r'<\$(.*?)\$>', template)
        input_keys = [key.strip() for key in parse_input_keys]

        # TODO: Extract output text should be general
        start_output_line_index = template.find('You should only respond')
        output_text = template[start_output_line_index + 1:]
        output = parse_semi_formatted_text(output_text)
        output_keys = list(output.keys())

        return template, input_keys, output_keys