from basic_module import *
import pandas as pd
import logging
import traceback
import re

def cut_and_merge(df, first_start_at, last_end_at, item_begin):
    errorcode = default_error_code
    error_message = default_error_message
    try:
        # 时间戳
        first_start_at = first_start_at * \
                         1000 if len(str(first_start_at)) == 10 else first_start_at
        last_end_at = last_end_at * \
                      1000 if len(str(last_end_at)) == 10 else last_end_at
        item_begin = item_begin * \
                     1000 if len(str(item_begin)) == 10 else item_begin

        df['begin_time'] = df['begin_time'] + item_begin
        df['end_time'] = df['end_time'] + item_begin
        df = df[df.begin_time >= first_start_at]
        df = df[df.end_time <= last_end_at]
        df['begin_time'] = df['begin_time'] - first_start_at
        df['end_time'] = df['end_time'] - first_start_at

        if df.shape[0] > 0:
            first_line = df.iloc[0]
            blank = {"begin_time": [0], "end_time": [0], "sentence_id": [1], "text": [""], 'textLength': [0],
                     'timeLength': [0]}
            if first_line.begin_time != 0:
                if first_line.text == '':
                    blank['end_time'][0] = first_line.end_time
                    blank['timeLength'][0] = blank['end_time'][0]
                    blank = pd.DataFrame(blank)
                    cut_df = pd.concat([blank, df[1:]])
                else:
                    blank['end_time'][0] = first_line.begin_time - 1
                    blank['timeLength'][0] = blank['end_time'][0]
                    blank = pd.DataFrame(blank)
                    cut_df = pd.concat([blank, df])
                cut_df['sentence_id'] = range(1, cut_df.shape[0] + 1)
            else:
                cut_df = df
        else:
            cut_df = df
    except:
        errorcode = jabber_error
        cut_df = df
        error_message = '算法失败，细节:{}'.format(traceback.format_exc())
    if cut_df.shape[0] == 0:
        errorcode = input_error
        error_message = '截取后文本为空'
    return cut_df, errorcode,error_message


def parseJsonToDf(jsonStr, which='teacher'):
    '''
    json to df
    :param jsonStr:
    :param which:
    :return:
    '''

    df, params, errorcode,errormsg = None, None, default_error_code,default_error_message
    if errorcode != success:
        return df, params, errorcode, jsonStr,errormsg

    params = jsonStr['class']
    params['first_start_at'] = int(params['first_start_at'])
    params['last_end_at'] = int(params['last_end_at'])
    first_start_at, last_end_at = params['first_start_at'], params['last_end_at']
    item_beign = int(jsonStr[which]['start_time_ms'])
    df, errorcode,errormsg = jsonParserMerge(jsonStr[which]['text'])
    if errorcode != success:
        return df, params, errorcode, jsonStr,errormsg
    df.fillna('', inplace=True)
    df, errorcode,errormsg = cut_and_merge(
        df, first_start_at, last_end_at, item_beign)
    if errorcode != success:
        return df, params, errorcode, jsonStr,errormsg
    df.fillna('', inplace=True)
    return df, params, errorcode, jsonStr,errormsg


def jsonParserMerge(jsonStr):
    if len(jsonStr) == 0:
        return None, text_empty,'文本为空'
    newMerge, errorcode,errormsg = None, default_error_code,default_error_message
    try:
        df = pd.DataFrame(jsonStr)
        df.drop_duplicates(['begin_time', 'end_time', 'text'],
                           inplace=True)
        # add two lines to convert all the timestamp into int
        df['begin_time'] = df['begin_time'].apply(lambda x: int(x))
        df['end_time'] = df['end_time'].apply(lambda x: int(x))
        df['status_code'] =0
        newDf = df[df.text != '']
        if newDf.shape[0]==0:
            return None,input_error,'输入文本为空'
        index = []
        index.extend((newDf.begin_time).tolist())
        blankStart = [0]
        blankStart.extend((newDf.iloc[:-1].end_time).tolist())
        blankEnd = newDf.begin_time
        blank = [{"begin_time": x[0], "end_time": x[1], "status_code": 0, "text": ""} for x in
                 zip(blankStart, blankEnd)]
        df_blank = pd.DataFrame(blank)
        newMerge = pd.concat([df_blank, newDf])
        newMerge = newMerge[newMerge.begin_time != newMerge.end_time].copy()
        newMerge.sort_values('begin_time', inplace=True)
        newMerge['sentence_id'] = range(1, newMerge.shape[0] + 1)
        newMerge['timeLength'] = newMerge.end_time - newMerge.begin_time
        compiled_rule = re.compile(r'[^\w]|_')
        newMerge['textLength'] = newMerge.text.apply(
            lambda x: len(compiled_rule.sub('', str(x))))
        newMerge = newMerge[['sentence_id', 'begin_time',
                             'end_time', 'timeLength', 'textLength', 'text']]
        newMerge = newMerge.copy()
    except:
        errormsg = traceback.format_exc()
        logging.error('Error parser jsonStr,detail is \n{}'.format(errormsg))
        errorcode = jabber_error
    return newMerge, errorcode,errormsg


if __name__ == '__main__':
    test_file_path = 'data/test_data/107716.json'
    df, params, errorcode, jsonStr = parseJsonToDf(
        open(test_file_path, 'r').read())
    print(errorcode)
