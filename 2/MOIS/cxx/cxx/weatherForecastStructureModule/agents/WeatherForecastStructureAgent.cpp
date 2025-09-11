#include <sc-agents-common/utils/IteratorUtils.hpp>
#include <sc-agents-common/utils/AgentUtils.hpp>
#include <curl/curl.h>
#include <nlohmann/json.hpp>
#include <sstream>
#include <algorithm>
#include "WeatherForecastStructureAgent.hpp"

using namespace std;
using namespace utils;
using namespace nlohmann;

namespace weatherForecastStructureModuleNS
{
    static size_t WriteCallback(void *contents, size_t size, size_t nmemb, string *s)
    {
        s->append((char *)contents, size * nmemb);
        return size * nmemb;
    }
    SC_AGENT_IMPLEMENTATION(WeatherForecastStructureAgent)
    {

        if (!m_memoryCtx.HelperCheckEdge(StructureKeynodes::action_fill_weather_forecast_structure, otherAddr, ScType::EdgeAccessConstPosPerm))
            return SC_RESULT_OK;
        SC_LOG_INFO("WeatherForecastStructureAgent: started");
        ScAddr addr = otherAddr;
        ScAddr const &keynode_rrel_1 = m_memoryCtx.HelperFindBySystemIdtf("rrel_1");

        
        ScAddr inputStr = IteratorUtils::getAnyByOutRelation(&m_memoryCtx, addr, keynode_rrel_1);
        if (!inputStr.IsValid())
        {
            SC_LOG_INFO("Недействительная входная структура");
            return SC_RESULT_ERROR;
        }

        
        ScAddr conceptCity = m_memoryCtx.HelperFindBySystemIdtf("concept_city");

        ScIterator3Ptr cityFinder = m_memoryCtx.Iterator3(
            conceptCity,
            ScType::EdgeAccessConstPosPerm,
            ScType::NodeConst);
        ScAddr city;
        while (cityFinder->Next())
        {
            city = cityFinder->Get(2);
            break;
        }
        if (!city.IsValid())
        {
            SC_LOG_INFO("Город не найден");
            return SC_RESULT_ERROR;
        }
        string cityName = m_memoryCtx.HelperGetSystemIdtf(city);
        SC_LOG_INFO("city: " + cityName);
        
        ScAddr conceptDate = m_memoryCtx.HelperFindBySystemIdtf("concept_date");
        ScIterator3Ptr dataFinder = m_memoryCtx.Iterator3(
            conceptDate,
            ScType::EdgeAccessConstPosPerm,
            ScType::NodeConst);
        ScAddr inputDate;
        while (dataFinder->Next())
        {
            inputDate = dataFinder->Get(2);
            break;
        }
        if (!inputDate.IsValid())
        {
            SC_LOG_INFO("Дата не найдена");
            return SC_RESULT_ERROR;
        }
        string dateValue = m_memoryCtx.HelperGetSystemIdtf(inputDate);
        replace(dateValue.begin(), dateValue.end(), '_', '-');
        SC_LOG_INFO("date: " + dateValue);
        
        CURL *curl = curl_easy_init();
        string response;
        if (curl)
        {
            string url = "https://api.openweathermap.org/data/2.5/forecast?q=" + cityName + "&appid=759744f91c07a1a23ca204b422f4a287&units=metric";
            curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
            curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCallback);
            curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response);
            CURLcode res = curl_easy_perform(curl);
            curl_easy_cleanup(curl);
            if (res != CURLE_OK)
            {
                SC_LOG_INFO("Ошибка при получении данных о погоде");
                return SC_RESULT_ERROR;
            }
        }

       
        json j = json::parse(response, nullptr, false);
        if (j.is_discarded())
        {
            SC_LOG_INFO("Недействительный JSON-ответ");
            return SC_RESULT_ERROR;
        }

        
        bool found = false;
        
        float maxPop = 0.0f;
        int count = 0;

        for (const auto &item : j["list"]) {
            string dt_txt = item["dt_txt"].get<string>();
            if (dt_txt.find(dateValue.substr(0, 10)) != string::npos) { // Сравниваем дату (YYYY-MM-DD)
                found = true;
                //float windSpeed = item["wind"]["speed"].get<float>();
                float pop = item.value("pop", 0.0f);
                //windSpeedSum += windSpeed;
                maxPop = max(maxPop, pop);
                count++;
                //SC_LOG_INFO("Временная точка: " + dt_txt + ", windSpeed: " + to_string(windSpeed) + ", pop: " + to_string(pop));
                SC_LOG_INFO("Временная точка: " + dt_txt + ", pop: " + to_string(pop));
            }
        }

        if (!found)
        {
            SC_LOG_INFO("Прогноз для указанной даты не найден");
            return SC_RESULT_ERROR;
        }
        //float avgWindSpeed = windSpeedSum / count;
        bool isRain = maxPop >= 0.5;
        //SC_LOG_INFO("Итоговые значения: avgWindSpeed: " + /*to_string(avgWindSpeed)*/ + ", isRain: " + (isRain ? "True" : "False"));
        SC_LOG_INFO("Итоговое значение: isRain: ");
        SC_LOG_INFO((isRain ? "True" : "False"));


        
        /*ScAddr conceptWindSpeed = m_memoryCtx.HelperFindBySystemIdtf("concept_wind_speed");
        ScIterator3Ptr windIt = m_memoryCtx.Iterator3(
            conceptWindSpeed,
            ScType::EdgeAccessConstPosPerm,
            ScType::NodeConst);

        ScAddr windNode;
        while (windIt->Next())
        {
            windNode = windIt->Get(2);
            break;
        }
        if (!windNode.IsValid())
        {
            SC_LOG_INFO("Узел скорости ветра не найден");
            return SC_RESULT_ERROR;
        }
        m_memoryCtx.HelperSetSystemIdtf(to_string(avgWindSpeed), windNode);
        */
        // Находим узел дождя через nrel_rain
        ScAddr conceptRain = m_memoryCtx.HelperFindBySystemIdtf("concept_rain");
        ScIterator3Ptr rainIt = m_memoryCtx.Iterator3(
            conceptRain,
            ScType::EdgeAccessConstPosPerm,
            ScType::NodeConst);
        ScAddr rainNode;
        while (rainIt->Next())
        {
            rainNode = rainIt->Get(2);
            break;
        }
        if (!rainNode.IsValid())
        {
            SC_LOG_INFO("Узел дождя не найден");
            return SC_RESULT_ERROR;
        }
        if(m_memoryCtx.HelperSetSystemIdtf(isRain ? "True" : "False", rainNode) == false)
        {
            std::string is_rain = isRain ? "True" : "False";
            ScAddr trueNode = m_memoryCtx.HelperFindBySystemIdtf(is_rain);
            ScAddr nrelRainNode = m_memoryCtx.HelperFindBySystemIdtf("nrel_rain");

            ScAddr arcFromConceptRain = m_memoryCtx.CreateEdge(ScType::EdgeAccessConstPosPerm, conceptRain, trueNode);
            

            ScAddr conceptWeather = m_memoryCtx.HelperFindBySystemIdtf("concept_weather");
            ScIterator3Ptr weatherIt = m_memoryCtx.Iterator3(
            conceptWeather,
            ScType::EdgeAccessConstPosPerm,
            ScType::NodeConst);
            weatherIt->Next();
            
            ScAddr arcFromWeatherNode = m_memoryCtx.CreateEdge(ScType::EdgeDCommonConst, weatherIt->Get(2), trueNode);  
            ScAddr arcToWeatherNodeArc = m_memoryCtx.CreateEdge(ScType::EdgeAccessConstPosPerm, nrelRainNode, arcFromWeatherNode);

            m_memoryCtx.CreateEdge(ScType::EdgeAccessConstPosPerm, inputStr, trueNode);
            m_memoryCtx.CreateEdge(ScType::EdgeAccessConstPosPerm, inputStr, arcFromConceptRain);
            m_memoryCtx.CreateEdge(ScType::EdgeAccessConstPosPerm, inputStr, arcFromWeatherNode);
            m_memoryCtx.CreateEdge(ScType::EdgeAccessConstPosPerm, inputStr, arcToWeatherNodeArc);
            m_memoryCtx.EraseElement(rainNode);

        }
        SC_LOG_INFO("WeatherForecastStructureAgent: finished");
        utils::AgentUtils::finishAgentWork(&m_memoryCtx, otherAddr, true);
        return SC_RESULT_OK;
    }

}