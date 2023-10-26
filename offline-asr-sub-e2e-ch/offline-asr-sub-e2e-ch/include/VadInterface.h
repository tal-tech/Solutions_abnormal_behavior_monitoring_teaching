//
// Created by alex on 19-2-18.
//

#ifndef VAD_DEMO_VADINTERFACE_H
#define VAD_DEMO_VADINTERFACE_H

#include <string>
#include <common_audio/vad/include/webrtc_vad.h>
#include <map>
#include <memory>
#include <vector>

#include "common.h"
#include "vadparamdefine.h"

namespace VadInterface{
class Vad {
public:

    /*
      @param : audio_data 音频数据起始地址
      @param : data_size  音频数据长度，字节
    */
    Vad(int16_t * audio_data, uint64_t data_size):web_vad(nullptr),
        audio_data(audio_data), data_size(data_size), data_pos(44),
        is_init(false),finish_cnt(0),sample_rate(16000),frame_size(160){}

    ~Vad();

    /*
      @desc  : 设置vad参数
      @param : params 通过VadParamLoader加载得到的vad参数，如果VadParamLoader加载失败，传入一个初始化的VadParams，Vad内部会使用默认参数
      @return: 失败返回false
    */
    bool Init(const VadParams& params);

    /*
      @desc  : 进行vad切分处理
      @param : periods 返回切分的片段信息，片段内的字段参见Period结构体的注释
      @return: 失败返回false,err_msg返回出错信息
    */
    bool Process(std::string &err_msg, std::vector<Period>& periods,const VadParams& params);

private:

    VadInst *VadCreate(const VadParams& params);

    void SmoothSpeech(uint64_t min_speech_length, uint64_t min_pre_silence, uint64_t min_after_silence, std::vector<Period>& periods);
    void SmoothSilence(uint64_t min_silence_length, uint64_t min_pre_speech, uint64_t min_after_speech, std::vector<Period>& periods);

    int ReadInt16Bytes(int16_t * &output);
    void WriteVadlistCutWav_new(std::string &pred_list, std::vector<Period>& periods);
    void WriteVadlistCutWav(std::string &pred_list, std::vector<Period>& periods);
    inline double calTimeByFrame(int64_t frame){ return (MULTI * frame * 10); }

    VadInst * web_vad;
    int16_t* audio_data;
    uint64_t data_size;
    uint64_t data_pos;
    bool is_init;
    size_t finish_cnt;

    int sample_rate;//采样率，默认16000
    int frame_size;//帧长：一帧对应的数据个数，默认取10ms长度(20ms/30ms备选)，10毫秒长度下为(sampleRate/100)
};
}

#endif //VAD_DEMO_VADINTERFACE_H
