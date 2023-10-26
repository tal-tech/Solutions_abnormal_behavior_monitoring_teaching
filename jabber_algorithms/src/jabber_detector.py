import sys
import os

basePath = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(basePath, 'tools'))
import util_tools
import core_funs
from basic_module import *



def check_input(student_json, teacher_json=None, student_start_at=0, teacher_start_at=0, task_id=''):
    error_code = default_error_code
    error_message = default_error_message
    result = {}
    error_code_student, error_message_student = util_tools.check_input_text(
        student_json)

    if error_code_student != 0:
        error_code = error_code_student
        error_message = error_message_student
        
    if not teacher_json is None and error_code==0:
        error_code_teacher, error_message_teacher = util_tools.check_input_text(
            teacher_json)
        if error_code_teacher != 0 and not teacher_json is None:
            error_code = error_code_teacher
            error_message = error_message_teacher
    
    return error_code, error_message, result


def jabber_detector(student_json, teacher_json=None, student_start_at=0, teacher_start_at=0, task_id=''):
    logger.info('Start - task_id:{}'.format(task_id))
    error_code, error_message,result = check_input(
        student_json, teacher_json, student_start_at, teacher_start_at, task_id)
    if error_code == 0:
        jsonStr = util_tools.change_input_2_godeye(student_json, teacher_json, student_start_at, teacher_start_at,
                                               task_id=task_id)
        logger.info("task_id:{} - jsonStr class info:{}".format(task_id,jsonStr['class']))
        error_code, error_message, result = core_funs.get_course_jabberTS_ms(
            jsonStr, teacher_json, task_id=task_id)
    logger.info('Finish - task_id:{},error_code:{},error_message:{}'.format(task_id,error_code,error_message))
    return {'error_code': error_code, 'error_message': error_message, 'result': result}

if __name__=="__main__":
    result=jabber_detector("./tools/test.json")
    print(result)
