/*
* This source file is part of an OSTIS project. For the latest info, see http://ostis.net
* Distributed under the MIT License
* (See accompanying file COPYING.MIT or copy at http://opensource.org/licenses/MIT)
*/

#include "weatherForecastStructureModule.hpp"
#include "keynodes/StructureKeynodes.hpp"
#include "agents/WeatherForecastStructureAgent.hpp"
#include "agents/WeatherRecommendationAgent.hpp"

using namespace weatherForecastStructureModuleNS;

SC_IMPLEMENT_MODULE(weatherForecastStructureModule)

sc_result weatherForecastStructureModule::InitializeImpl()
{
  if (!weatherForecastStructureModuleNS::StructureKeynodes::InitGlobal())
    return SC_RESULT_ERROR;

  SC_AGENT_REGISTER(WeatherForecastStructureAgent)
  SC_AGENT_REGISTER(WeatherRecommendationAgent)

  return SC_RESULT_OK;
}

sc_result weatherForecastStructureModule::ShutdownImpl()
{

  SC_AGENT_UNREGISTER(WeatherForecastStructureAgent)
  SC_AGENT_UNREGISTER(WeatherRecommendationAgent)

  return SC_RESULT_OK;
}
