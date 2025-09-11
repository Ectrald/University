#pragma once

#include <sc-memory/kpm/sc_agent.hpp>
#include "keynodes/StructureKeynodes.hpp"

#include "WeatherRecommendationAgent.generated.hpp"
namespace weatherForecastStructureModuleNS {
  class WeatherRecommendationAgent : public ScAgent {
    SC_CLASS(Agent, Event(StructureKeynodes::question_initiated, ScEvent::Type::AddOutputEdge))
    SC_GENERATED_BODY()
private:
    
  };

} // namespace weatherForecastStructureModuleNS