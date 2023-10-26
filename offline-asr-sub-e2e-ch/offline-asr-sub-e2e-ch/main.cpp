#include<iostream>
#include "include/tal_asr_api.h"
#include "include/tal_asr_define.h"
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <base/base64.h>
#include <vector>
#include <fstream>
//模型结构体
struct AlgModInstance
{
    int mode_id;
    void* mode_ptr;
};
//全局变量模型实例句柄
void * asr_resource = nullptr;
AlgModInstance* globle_alg_ptr;
void Init() 
{
    const char *mod_dir = "../../../res";//模型路径
    
    int ret = TalASRResourceImport(mod_dir, &asr_resource);// 资源初始化状态, 0表示初始化成功, 其它表示异常
    if(ret != 0 || !asr_resource) 
    {
        std::cout << "failed to load alg mod ret: " << ret << std::endl;
        exit(1);
    }
    //创建一个ASR实例 0表示创建成功, 其它表示失败
    void* dec = NULL;
    ret = TALASRInstanceCreate(asr_resource, &dec);
    if(ret != 0 || !dec)
    {
        std::cout << "asr create failed:" << ret<< std::endl;
        return;
    }
    //ASR实例运行设置
    if((ret = TalASRInstanceStart(dec, "")))
    {
        std::cout << "asr started failed:" << ret<< std::endl;
        return;
    }
    //将模型实例传给全局变量
    globle_alg_ptr = new AlgModInstance;
    globle_alg_ptr->mode_ptr = dec;
    globle_alg_ptr->mode_id = 0;
    //获取ASR资源版本
    std::string version = TalASRResourceGetVersion(asr_resource);
    std::cout << "Resourc version:" << version << std::endl;
}
/*
 * brief  ASR实例识别
 * @param [in] asr_instance, ASR实例句柄
 * @param [in] wav_data, wav音频数据
 * @param [in] wav_data_len, wav音频数据长度, 单位字节, 最长限制3分钟,
 * 超过3分钟会强制切成3分钟为单位进行识别
 * @param [out] result, 识别结果, json格式
 * @param [out] 识别状态值, 0表示本次识别正常, 其它表示异常
*/
void getResult(std::string voicePath,std::string &result_list)
{
    //从文件读取数据的输入流类。ifstream 代表“input file stream”，它是 std::istream 的派生类，用于从文件中读取数据
    std::ifstream audioFileStream(voicePath, std::ios::binary);
    if (!audioFileStream) 
    {
        std::cerr << "Failed to open audio file." << std::endl;
        return;
    }
    //从已打开的 audioFileStream 文件流中读取数据，并将其存储在 audioData 变量
    std::string audioData((std::istreambuf_iterator<char>(audioFileStream)),std::istreambuf_iterator<char>());
    audioFileStream.close();//关闭文件流
    //base64编码
    std::string b64Data;
    base::Base64Encode(audioData, &b64Data);
    // Base64解码
    std::string data_str = "";
    base::Base64Decode(b64Data, &data_str);
    //调用模型进行语音识别
    int ret = TalASRInstanceRecognize(globle_alg_ptr->mode_ptr, (char *)data_str.c_str(), data_str.length(), result_list);
    return;
}
std::string extractResult(const std::string& input) 
{
    std::string resultField = "\"result\":\"";
    size_t startPos = input.find(resultField);
    if (startPos == std::string::npos) 
    {
        return "";  
    }
    startPos += resultField.length();
    size_t endPos = input.find("\"", startPos);
    if (endPos == std::string::npos) 
    {
        return "";  
    }

    return input.substr(startPos, endPos - startPos);
}
int main()
{
    std::string path = "../../../testVoice.wav";
    std::string result;
    //初始化模型
    Init();
    //获取结果
    getResult(path, result);
    //处理结果获取中文语句
    result = extractResult(result);
    std::cout << result << std::endl;
    return 0;
}