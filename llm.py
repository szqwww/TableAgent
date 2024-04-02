
import inspect

def run_conversation(messages, functions_list=None, model="gpt-3.5-turbo"):
    """
    能够自动执行外部函数调用的Chat对话模型
    :param messages: 必要参数，字典类型，输入到Chat模型的messages参数对象
    :param functions_list: 可选参数，默认为None，可以设置为包含全部外部函数的列表对象
    :param model: Chat模型，可选参数，默认模型为gpt-3.5
    :return：Chat模型输出结果
    """

    from openai import OpenAI
    client = OpenAI(base_url=api_url,api_key=api_key)

    # 如果没有外部函数库，则执行普通的对话任务

    if functions_list == None:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
        )
        response_message = response.choices[0].message
        final_response = response_message.content

    # 若存在外部函数库，则需要灵活选取外部函数并进行回答
    else:
        # 创建functions对象
        tools = auto_functions(functions_list)

        available_functions = {func.__name__: func for func in functions_list}


        # first response
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice="auto")
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        # 判断返回结果是否存在function_call，即判断是否需要调用外部函数来回答问题
        if tool_calls:
            # 需要调用外部函数
            # 创建外部函数库字典
            available_functions = {func.__name__: func for func in functions_list}

            for tool_call in tool_calls:
                function_name = tool_call.function.name
                # 获取函数对象
                function_to_call = available_functions[function_name]
                # 获取函数参数
                function_args = json.loads(tool_call.function.arguments)
                # 将函数参数输入到函数中，获取函数计算结果
                function_response = function_to_call(**function_args)

                # messages中拼接first response消息
                messages.append(response_message)

                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": function_response,
                    }
                )
                # 第二次调用模型

            second_response = client.chat.completions.create(
                model=model,
                messages=messages,
            )
            # 获取最终结果
            final_response = second_response.choices[0].message.content
        else:
            final_response = response_message.content

    return final_response




