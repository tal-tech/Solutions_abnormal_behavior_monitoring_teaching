from basic_module import *


def get_jsonStr_duration(jsonStr):
    text_list = jsonStr
    if len(text_list) == 0:
        return 0
    else:
        duration = int(text_list[-1]['end_time'])
        return duration

def check_input_text(text_list):
    error_code = default_error_code
    error_message = default_error_message

    if len(text_list) == 0:
        error_code = input_error
        error_message = 'text list is empty'

    for item in text_list:
        if type(item)!=dict:
            error_code = input_error
            error_message = 'text_list item not json'
            break
        else:
            for key in ['text','begin_time','end_time']:
                if key not in item:
                    error_code = input_error
                    error_message = '缺少{}'.format(key)
                    break

    if len(''.join([x['text'] for x in text_list]))==0:
        error_code = input_error
        error_message = '输入的文本为空'

    return error_code, error_message

def change_input_2_godeye(student_json, teacher_json, student_start_at=0, teacher_start_at=0, subject=12, task_id=''):

    if teacher_json is None:
        first_start_at = 0
        teacher_start_at = 0
        student_start_at = 0
    else:
        first_start_at = max(student_start_at, teacher_start_at)

    jsonStr = {
        "class": {
            "first_start_at": first_start_at,
            "last_end_at": 0,
            "subject": subject,
            "id": task_id
        },
        "student": {
            "duration": get_jsonStr_duration(student_json),
            "start_time_ms": student_start_at,
            "text": student_json
        },
        "teacher": {
            "duration": 0,
            "start_time_ms": teacher_start_at,
            "text": []
        }
    }

    if teacher_json is None:
        jsonStr['teacher'] = {}
        jsonStr['class']['last_end_at'] = jsonStr['class']['first_start_at'] + jsonStr['student']['duration']

    else:
        jsonStr['teacher']['duration'] = get_jsonStr_duration(teacher_json)
        jsonStr['class']['last_end_at'] = min(student_start_at+jsonStr['student']['duration'],
                                              teacher_start_at+jsonStr['teacher']['duration'])
        jsonStr['teacher']['text'] = teacher_json
    return jsonStr


def parse_list_2_df(text, task_id=''):
    error_code = default_error_code
    error_message = default_error_message
    df = None
    if len(text) == 0:
        error_code = text_empty
        logger.info('task_id:{},input text len is 0'.format(task_id))
        return error_code, error_message, df
    else:
        try:
            df = pd.DataFrame(text)
            df['sentence_id'] = range(1, df.shape[0] + 1)
            df['timeLength'] = df.end_time - df.begin_time
            df['textLength'] = df.text.apply(lambda x: len(re_no_char.sub('', str(x))))
        except:
            logger.error('task_id:{},input format error,detail is{}'.format(task_id, traceback.format_exc()))
            error_code = input_error
        return error_code, error_message, df
