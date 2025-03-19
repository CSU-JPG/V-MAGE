import os
import re
import math
import base64
from PIL import Image
from io import BytesIO
from typing import Any, Dict, List

from utils.encoding_utils import encode_image_path

def get_torch_dtype(torch_dtype):
    import torch
    if torch_dtype == 'bfloat16':
        return torch.bfloat16
    elif torch_dtype == 'float16':
        return torch.float16
    else:
        # TODO
        pass

def load_image_from_base64(base64_str):
    image_data = base64.b64decode(base64_str)
    image = Image.open(BytesIO(image_data))
    # 可以添加需要的图像预处理逻辑，比如调整大小等
    return image

def placeholder_process(paragraph, params):
    
    search_placeholder_pattern = re.compile(r"<\$[^\$]+\$>")
    placeholders = search_placeholder_pattern.findall(paragraph)

    for placeholder in placeholders:
        placeholder_name = placeholder.replace("<$", "").replace("$>", "")
        paragraph_input = params.get(placeholder_name, None)

        if paragraph_input is None or paragraph_input == "" or paragraph_input == []:
            paragraph = paragraph.replace(placeholder, "")
            
        else:
            if isinstance(paragraph_input, str):
                paragraph = paragraph.replace(placeholder, paragraph_input)
            elif isinstance(paragraph_input, list):
                paragraph = paragraph.replace(placeholder, str(paragraph_input))
            else:
                raise ValueError(f"Unexpected input type: {type(paragraph_input)}")

    return paragraph

def assemble_prompt(template_str: str = None, params: Dict[str, Any] = None, image_prompt_format="openai") -> List[Dict[str, Any]]:

        """
        A tripartite prompt is a message with the following structure:
        <system message> \n\n
        <message part 1>
        <image paragraph>
        <message part 2>
        <image paragraph>
        <message part 2>
        ...
        """
        pattern = re.compile(r"(.+?)(?=\n\n|$)", re.DOTALL)
        # 段落之间由双换行符分隔

        paragraphs = re.findall(pattern, template_str)

        filtered_paragraphs = [p for p in paragraphs if p.strip() != '']

        system_content = filtered_paragraphs[0]  # the system content defaults to the first paragraph of the template
        system_content = placeholder_process(system_content, params)
        
        if image_prompt_format in ["claude"]:
            system_message = {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"{system_content}"
                    }
                ]
            }
        else:
            system_message = {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": f"{system_content}"
                    }
                ]
            }

        user_messages_contents = []
        
        user_messages = []
        
        debug = False
        
        for paragraph in filtered_paragraphs[1:]:
            # placeholder that start with "<$image" and end with "$>" will be treated as image placeholder
            image_placeholder_match = re.search(r'<\$image(.*?)\$>', paragraph)
            if image_placeholder_match:
                image_placeholder = image_placeholder_match.group(0).replace("<$", "").replace("$>", "")
                assert image_placeholder in params
                
                if len(user_messages_contents) > 0:
                    user_messages_content = ("\n\n".join(user_messages_contents))

                    user_messages.append({
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"{user_messages_content}"
                            }
                        ]
                    })
                    user_messages_contents = []
            
                # TODO text at front/behind of the image, should be seperated.
                paragraph_text_content = paragraph.replace(f"<${image_placeholder}$>", "")
                paragraph_text_content = placeholder_process(paragraph_text_content, params)
                
                message = {
                    "role": "user",
                    "content": []
                }
                if paragraph_text_content.strip() != '':
                    msg_content = {
                        "type": "text",
                        "text": f"{paragraph_text_content}"
                    }
                    message["content"].append(msg_content)
                
                image_item = params.get(image_placeholder)
                if os.path.isfile(image_item):
                    encoded_image = encode_image_path(image_item)
                    image_type = image_item.split(".")[-1].lower()
                    image_item = f"data:image/{image_type};base64,{encoded_image}"
                    
                else:
                    if image_item.startswith('data:image/'):
                        pass
                    else:
                        # TODO deafult png
                        image_item = f"data:image/png;base64,{image_item}"
                # image_item = str(image_item)
                
                if debug:
                    image_item = image_item[:30] + ".." + image_item[100:110] + "..." + image_item[200:210] + "..." + image_item[-10:]
                        
                if image_prompt_format in ["openai"]:
                    msg_content = {
                        "type": "image_url",
                        "image_url": {
                            "url": f"{image_item}"
                        }
                            
                    }
                elif image_prompt_format in ["claude"]:
                    msg_content = {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": image_item.split("base64,")[1]
                            # DEBUG
                            # "data": image_item.split("base64,")[1][:10]
                        }
                    }
                else:
                    msg_content = {
                        "type": "image",
                        "image": f"{image_item}"     
                    }
                    
                message["content"].append(msg_content)
                                
                if len(message["content"]) > 0:
                    user_messages.append(message)  
            else:
                paragraph = placeholder_process(paragraph, params)
                user_messages_contents.append(paragraph)
  

        if len(user_messages_contents) > 0:

            user_messages_content = ("\n\n".join(user_messages_contents))

            user_messages.append({
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"{user_messages_content}"
                    }
                ]
            })

        return [system_message] + user_messages

def convert_openai_messages(original_messages):
    """
    将OpenAI格式的messages转换为新的消息格式和图像数组
    
    Args:
        original_messages (list): OpenAI格式的消息列表，示例格式：
            [{
                "role": "user",
                "content": [
                    {"type": "text", "text": "问题文本"},
                    {"type": "image_url", "image_url": {"url": "data:image/png;base64,..."}}
                ]
            }]
    
    Returns:
        tuple: (images, new_messages)
            images (list): PIL.Image对象列表
            new_messages (list): 新格式的消息列表，示例格式：
                [{
                    "role": "user",
                    "content": "问题文本\n<image_start><image><image_end>..."
                }]
    """
    images = []
    new_messages = []
    
    for msg in original_messages:
        if msg["role"] == "user":
            text_parts = []
            image_count = 0
            
            # 解析原始内容
            for content in msg["content"]:
                if content["type"] == "text":
                    text_parts.append(content["text"])
                elif content["type"] == "image_url":
                    # 解码base64图像
                    header, data = content["image_url"]["url"].split(",", 1)
                    image_data = base64.b64decode(data)
                    image = Image.open(BytesIO(image_data)).convert("RGB")
                    images.append(image)
                    image_count += 1
            
            # 构建新消息内容
            new_content = "\n".join(text_parts)
            if image_count > 0:
                image_tags = "".join(["<image_start><image><image_end>" for _ in range(image_count)])
                new_content += "\n" + image_tags
                
            new_messages.append({
                "role": msg["role"],
                "content": new_content
            })
        else:
            text_parts = []
            for content in msg["content"]:
                if content["type"] == "text":
                    text_parts.append(content["text"])
            new_content = "\n".join(text_parts)
                    
            new_messages.append({
                "role": msg["role"],
                "content": new_content
            })
    
    return images, new_messages



# Swift Utils
def swift_process_json_data(messages, torch_dtype):
    torch_dtype = get_torch_dtype(torch_dtype)
    
    question = ""
    images = []
    question_parts = []
    
    # 遍历 JSON 数据中的所有消息
    for message in messages:
        role = message['role']  # 获取消息的角色
        
        for content in message['content']:
            
            if content['type'] == 'image':
                # 处理图像
                image_base64 = content['image'].split(',')[1]
                images.append(image_base64)
                question_parts.append('<image>')
                
            elif content['type'] == 'text':
                question_parts.append(content['text'])
    
    # 拼接问题字符串
    question = '\n'.join(question_parts)
    
    return question, images

def load_swift_model(model_type, local_dir, torch_dtype,):
    
    from swift.llm import (
        get_model_tokenizer, get_template, get_default_template_type
    )


    template_type = get_default_template_type(model_type)

    torch_dtype = get_torch_dtype(torch_dtype)

    model, tokenizer = get_model_tokenizer(
        model_type, 
        torch_dtype,
        model_id_or_path=local_dir,
        model_kwargs={'device_map': 'auto'}
    )

    template = get_template(template_type, tokenizer)

    return model, template



# InternVL Utils
def internvl_split_model(model_name):
    
    import torch
    device_map = {}
    world_size = torch.cuda.device_count()
    num_layers = {
        'InternVL2-1B': 24, 'InternVL2-2B': 24, 'InternVL2-4B': 32, 'InternVL2-8B': 32,
        'InternVL2-26B': 48, 'InternVL2-40B': 60, 'InternVL2-Llama3-76B': 80}[model_name]
    # Since the first GPU will be used for ViT, treat it as half a GPU.
    num_layers_per_gpu = math.ceil(num_layers / (world_size - 0.5))
    num_layers_per_gpu = [num_layers_per_gpu] * world_size
    num_layers_per_gpu[0] = math.ceil(num_layers_per_gpu[0] * 0.5)
    # num_layers_per_gpu[0] = 0
    layer_cnt = 0
    for i, num_layer in enumerate(num_layers_per_gpu):
        for j in range(num_layer):
            device_map[f'language_model.model.layers.{layer_cnt}'] = i
            layer_cnt += 1
    device_map['vision_model'] = 0
    device_map['mlp1'] = 0
    device_map['language_model.model.tok_embeddings'] = 0
    device_map['language_model.model.embed_tokens'] = 0
    device_map['language_model.output'] = 0
    device_map['language_model.model.norm'] = 0
    device_map['language_model.lm_head'] = 0
    device_map[f'language_model.model.layers.{num_layers - 1}'] = 0

    return device_map

def load_internvl_model(cache_dir, model_path, model_split_name, torch_dtype, use_flash_attn, low_cpu_mem_usage, max_new_tokens):
    
    device_map = internvl_split_model(model_split_name)
    
    torch_dtype = get_torch_dtype(torch_dtype)
        
    use_flash_attn = use_flash_attn== "True"
    low_cpu_mem_usage = low_cpu_mem_usage == "True"
    max_new_tokens = int(max_new_tokens)
    
    from transformers import AutoModel, AutoTokenizer
    model = AutoModel.from_pretrained(
        model_path,
        torch_dtype=torch_dtype,
        low_cpu_mem_usage=low_cpu_mem_usage,
        use_flash_attn=use_flash_attn,
        trust_remote_code=True,
        device_map=device_map,
        cache_dir=cache_dir).eval()

    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True, use_fast=True, cache_dir=cache_dir)

    generation_config = dict(max_new_tokens=max_new_tokens, do_sample=True)
    
    return model, tokenizer, generation_config

def build_transform(input_size):
    import torchvision.transforms as T
    from torchvision.transforms.functional import InterpolationMode
    IMAGENET_MEAN = (0.485, 0.456, 0.406)
    IMAGENET_STD = (0.229, 0.224, 0.225)
    MEAN, STD = IMAGENET_MEAN, IMAGENET_STD
    transform = T.Compose([
        T.Lambda(lambda img: img.convert('RGB') if img.mode != 'RGB' else img),
        T.Resize((input_size, input_size), interpolation=InterpolationMode.BICUBIC),
        T.ToTensor(),
        T.Normalize(mean=MEAN, std=STD)
    ])
    return transform

def find_closest_aspect_ratio(aspect_ratio, target_ratios, width, height, image_size):
    best_ratio_diff = float('inf')
    best_ratio = (1, 1)
    area = width * height
    for ratio in target_ratios:
        target_aspect_ratio = ratio[0] / ratio[1]
        ratio_diff = abs(aspect_ratio - target_aspect_ratio)
        if ratio_diff < best_ratio_diff:
            best_ratio_diff = ratio_diff
            best_ratio = ratio
        elif ratio_diff == best_ratio_diff:
            if area > 0.5 * image_size * image_size * ratio[0] * ratio[1]:
                best_ratio = ratio
    return best_ratio

def dynamic_preprocess(image, min_num=1, max_num=12, image_size=448, use_thumbnail=False):
    orig_width, orig_height = image.size
    aspect_ratio = orig_width / orig_height

    # calculate the existing image aspect ratio
    target_ratios = set(
        (i, j) for n in range(min_num, max_num + 1) for i in range(1, n + 1) for j in range(1, n + 1) if
        i * j <= max_num and i * j >= min_num)
    target_ratios = sorted(target_ratios, key=lambda x: x[0] * x[1])

    # find the closest aspect ratio to the target
    target_aspect_ratio = find_closest_aspect_ratio(
        aspect_ratio, target_ratios, orig_width, orig_height, image_size)

    # calculate the target width and height
    target_width = image_size * target_aspect_ratio[0]
    target_height = image_size * target_aspect_ratio[1]
    blocks = target_aspect_ratio[0] * target_aspect_ratio[1]

    # resize the image
    resized_img = image.resize((target_width, target_height))
    processed_images = []
    for i in range(blocks):
        box = (
            (i % (target_width // image_size)) * image_size,
            (i // (target_width // image_size)) * image_size,
            ((i % (target_width // image_size)) + 1) * image_size,
            ((i // (target_width // image_size)) + 1) * image_size
        )
        # split the image
        split_img = resized_img.crop(box)
        processed_images.append(split_img)
    assert len(processed_images) == blocks
    if use_thumbnail and len(processed_images) != 1:
        thumbnail_img = image.resize((image_size, image_size))
        processed_images.append(thumbnail_img)
    return processed_images

def internvl_load_image(image_file, input_size=448, max_num=12):
    
    import torch
    # image = Image.open(image_file).convert('RGB')
    transform = build_transform(input_size=input_size)
    images = dynamic_preprocess(image_file, image_size=input_size, use_thumbnail=True, max_num=max_num)
    pixel_values = [transform(image) for image in images]
    pixel_values = torch.stack(pixel_values)
    return pixel_values

def internvl_process_json_data(messages, torch_dtype):
    import torch
    
    torch_dtype = get_torch_dtype(torch_dtype)
    
    pixel_values_list = []
    num_patches_list = []
    question_parts = []
    image_counter = 1
    
    # 遍历 JSON 数据中的所有消息
    for message in messages:
        role = message['role']  # 获取消息的角色
        
        for content in message['content']:
            
            if content['type'] == 'image':
                # 处理图像
                image_base64 = content['image'].split(',')[1]
                image = load_image_from_base64(image_base64)
                pixel_values = internvl_load_image(image, max_num=12).to(torch_dtype).cuda()
                pixel_values_list.append(pixel_values)
                num_patches_list.append(pixel_values.size(0))
                # 构造问题部分或历史中的图像标记
                question_parts.append('<image>')
                image_counter += 1
                
            elif content['type'] == 'text':
                question_parts.append(content['text'])
    
    # 拼接问题字符串
    question = '\n'.join(question_parts)
    
    # 拼接所有图像的张量
    if pixel_values_list:
        pixel_values = torch.cat(pixel_values_list, dim=0)
    else:
        pixel_values = None  # 如果没有图像，保持 None
    
    return question, pixel_values, num_patches_list


# Qwen2VL Utils
def load_qwen_model(cache_dir, model_path, torch_dtype):
    torch_dtype = get_torch_dtype(torch_dtype)
    from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
    
    model = Qwen2VLForConditionalGeneration.from_pretrained(
        # TODO device_map
        model_path, 
        torch_dtype=torch_dtype, 
        device_map="auto", 
        cache_dir=cache_dir
    )
    
    processor = AutoProcessor.from_pretrained(model_path, cache_dir=cache_dir)


    
    return model, processor