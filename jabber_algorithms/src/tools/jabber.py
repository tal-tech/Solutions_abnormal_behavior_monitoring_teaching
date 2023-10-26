import os
import sys
import pickle
import pandas as pd
import json
from basic_module import *
import jabberClassifierBiLstm
from util_tools import change_input_2_godeye
from jsonStrParserTool import parseJsonToDf

def getJabberTS_ms(course_text,course_id):
    try:
        logger.info("task_id:{},course_text len is {}".format(course_id,len(course_text)))
        course_jabber_label = jabberClassifierBiLstm.predict_jabber_sentence_list(course_text)
        jabberInd = np.array(course_jabber_label) == 1
        logging.info('course_id: {} - jabber sentence num is {}'.format(course_id, np.sum(jabberInd)))
        jabberTimestamp = [] if np.sum(
            jabberInd) == 0 else course_text[jabberInd].apply(
                lambda x: (x['begin_time'], x['end_time']), axis=1).tolist()
        jabberTimestamp = [{
            'start_ts_ms': value[0],
            'end_ts_ms': value[1],
            'index': index
        } for index, value in enumerate(jabberTimestamp)]
    except Exception as e:
        logging.error('jabber detect failed, detail is \n{}'.format(
            traceback.format_exc()))
        jabberTimestamp = []
    return jabberTimestamp


def process_input_data(jsonStr, teacher_json=None,task_id=''):
    logger.info('task_id:{},start parser student_text and teacher_text json data'.format(task_id))
    student_text, _, state_student, _ ,errormsg_student= parseJsonToDf(jsonStr, 'student')
    if not teacher_json is None:
        teacher_text, _, state_teacher, _ ,errormsg_teacher= parseJsonToDf(jsonStr, 'teacher')
    else:
        teacher_text = None
        errormsg_teacher = ''
        state_teacher = 0
    logger.info('task_id:{},finish parser student_text and teacher_text json data'.format(task_id))
    return state_student, state_teacher, student_text, teacher_text,errormsg_student,errormsg_teacher


def get_one_array(all_time_series, time_2_index, item_matrix,task_id=''):
    item_array = np.zeros(all_time_series.shape[0])
    for start_time, end_time, text_length in zip(
            item_matrix[:, 0], item_matrix[:, 1], item_matrix[:, 2]):
        bais = 0
        if end_time == all_time_series[-1]:
            bais = 1
        if text_length == 0:
            item_array[time_2_index[start_time]:time_2_index[end_time] + bais] = 0
        else:
            item_array[time_2_index[start_time]:time_2_index[end_time] + bais] = 1
    return item_array


def get_item_array(jsonStr, teacher_json=None, task_id=''):
    error_code = default_error_code
    error_message = default_error_message
    item_array = None
    item_duration = None
    index_2_time = None

    state_student, state_teacher, student_text, teacher_text,errormsg_student,errormsg_teacher = process_input_data(
        jsonStr, teacher_json,task_id=task_id)
    logger.info('task_id:{},state_teacher:{},state_student:{}'.format(task_id, state_teacher, state_student))
    if state_student != success:
        error_code = state_student
        error_message = errormsg_student
        return item_array, item_duration, index_2_time, error_code, error_message
    if state_teacher != success:
        error_code = state_teacher
        error_message = errormsg_teacher
        return item_array, item_duration, index_2_time, error_code, error_message
    student_matrix = student_text[['begin_time', 'end_time',
                                   'textLength']].as_matrix()
    if not teacher_json is None:
        teacher_matrix = teacher_text[['begin_time', 'end_time',
                                       'textLength']].as_matrix()

        item_text = pd.concat([teacher_text, student_text])
        item_matrix = np.vstack([teacher_matrix, student_matrix])
    else:
        item_text = student_text
        item_matrix = student_matrix
    # get item matrix
    item_matrix = item_matrix[item_matrix[:, 0].argsort()]
    # get item text
    item_text.sort_values(['begin_time', 'end_time'], inplace=True)
    item_text.fillna('', inplace=True)
    item_text = item_text[item_text.text != ''].copy()
    item_text.index = range(item_text.shape[0])
    # get all time series
    all_time_series = np.unique(
        np.hstack([item_matrix[:, 0], item_matrix[:, 1]]))
    all_time_series = all_time_series[all_time_series.argsort()]
    all_time_series = np.hstack([all_time_series[1:-1], all_time_series])
    all_time_series = all_time_series[all_time_series.argsort()]
    # get time 2 index
    time_2_index = dict(zip(all_time_series, range(all_time_series.shape[0])))
    index_2_time = dict(zip(range(all_time_series.shape[0]), all_time_series))
    # get item array
    student_array = get_one_array(all_time_series, time_2_index, student_matrix)
    # print(student_array)
    if not teacher_text is None:
        teacher_array = get_one_array(
            all_time_series, time_2_index, teacher_matrix)
        item_array = student_array + teacher_array
    else:
        item_array = student_array

    # get jabber
    item_jabber_list = getJabberTS_ms(item_text, task_id)
    for item_jabber in item_jabber_list:
        start_time = time_2_index[item_jabber['start_ts_ms']]
        end_time = time_2_index[item_jabber['end_ts_ms']]
        if item_jabber['end_ts_ms'] == all_time_series[-1]:
            item_array[start_time:] = 3
        else:
            item_array[start_time:end_time] = 3
    item_duration = all_time_series[-1]
    return item_array, item_duration, index_2_time, error_code, error_message


def get_course_jabberTS_ms(jsonStr, teacher_json=None, task_id=''):
    result = {}

    logger.info('task_id:{},Parser teacher and student'.format(task_id))
    item_array, item_duration, index_2_time, error_code, error_message = get_item_array(
        jsonStr, teacher_json, task_id)
    logger.info('task_id:{},Parser finish error_code is {}'.format(task_id, error_code))
    if error_code != success:
        error_code = error_code
        error_message = error_message
        logger.error('task_id:{},fail detail is {}'.format(task_id, traceback.format_exc()))
        return error_code, error_message, result
    result = {
        "silent_rate": 0,
        "normal_class_rate": 0,
        "jabber_rate": 0,
        "silent_duration_ms": 0,
        "normal_class_duration_ms": 0,
        "jabber_duration_ms": 0,
        "silent_ts_ms": [],
        "normal_class_ts_ms": [],
        "jabber_ts_ms": []
    }
    jabber_index_map = {
        0: 'silent_ts_ms',
        1: 'normal_class_ts_ms',
        2: 'normal_class_ts_ms',
        3: 'jabber_ts_ms',
        4: 'jabber_ts_ms',
        6: 'jabber_ts_ms'
    }
    # if teacher_student_array_merge.shape[0]
    jabber_status_last = item_array[0]
    start_index = 0
    end_index = 0
    for jabber_status_now, time_index_now in zip(
            item_array[1:], range(1, item_array.shape[0])):
        if jabber_index_map[jabber_status_now] != jabber_index_map[jabber_status_last]:
            result[jabber_index_map[jabber_status_last]].append({
                "start_ts_ms": int(index_2_time[start_index]),
                "end_ts_ms": int(index_2_time[end_index]),
            })
            start_index = time_index_now
            jabber_status_last = jabber_status_now
        else:
            end_index = time_index_now
    result[jabber_index_map[jabber_status_now]].append({
        "start_ts_ms": int(index_2_time[start_index]),
        "end_ts_ms": int(index_2_time[time_index_now]),
    })
    result['silent_rate'] = np.sum([x['end_ts_ms'] - x['start_ts_ms'] for x in result['silent_ts_ms']]) / item_duration
    result['normal_class_rate'] = np.sum(
        [x['end_ts_ms'] - x['start_ts_ms'] for x in result['normal_class_ts_ms']]) / item_duration
    result['jabber_rate'] = np.sum([x['end_ts_ms'] - x['start_ts_ms'] for x in result['jabber_ts_ms']]) / item_duration
    
    result['silent_duration_ms'] = int(result['silent_rate'] * item_duration)
    result['normal_class_duration_ms'] = int(result['normal_class_rate'] * item_duration)
    result['jabber_duration_ms'] = int(result['jabber_rate'] * item_duration)
    logger.info('Duration is {}'.format(item_duration))
    
    for item_ts in ['silent_ts_ms', 'normal_class_ts_ms', 'jabber_ts_ms']:
        for index, item in enumerate(result[item_ts]):
            item['index'] = index
    return error_code, error_message, result
