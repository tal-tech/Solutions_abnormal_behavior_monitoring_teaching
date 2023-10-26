#pragma once
/*
 * tal_asr_define.h
 *
 *  Created on: Stempber 14, 2020
 *      Author: yanzikui
 */
namespace TAL_ASR {
  enum TAL_ASR_STAT_CODE {
    TAL_ASR_OK = 0,
    TAL_ASR_ERROR = -1,
    TAL_ASR_CONFIG_FILE_NOT_FOUND = -101,
    TAL_ASR_CONFIG_VERSION_NOT_FOUND = -102,
    TAL_ASR_CONFIG_MODEL_NOT_FOUND = -103,
    TAL_ASR_CONFIG_DICT_NOT_FOUND = -104,
  };

  enum TAL_LANGUAGE {
    TAL_UNKNOWN = 0,
    TAL_MANDARIN = 1,  // 中文普通话
    TAL_ENGLISH = 2,   // 英文
    TAL_MANDARIN_ENGLISH = 4,   // 中英混合
  };
}
