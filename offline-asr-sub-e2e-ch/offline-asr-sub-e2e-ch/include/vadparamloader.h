#ifndef TLV_VAD_PARAM_LOADER_H_
#define TLV_VAD_PARAM_LOADER_H_

#include "vadparamdefine.h"

#include <vector>
#include <string>

namespace VadInterface {

class VadParamLoader {
public:
    VadParamLoader();
    ~VadParamLoader();

    /*
      @desc  : 加载资源下的vad_cfg.json文件，获取vad配置参数
      @param : file_path 资源目录下的vad_cfg.json文件全路径
      @param : params_out 返回vad参数
      @return: 如果vad_cfg.json文件不存在或文件加载失败，返回false,参数加载成功返回true
    */
    bool loadVadParams(const std::string& file_path, VadParams& params_out);

private:
    std::string readFileIntoString(const std::string& file_path);

};

}//namespace

#endif  // TLV_VAD_PARAM_LOADER_H_
