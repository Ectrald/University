/*
 * This source file is part of an OSTIS project. For the latest info, see
 * http://ostis.net Distributed under the MIT License (See accompanying file
 * COPYING.MIT or copy at http://opensource.org/licenses/MIT)
 */

#pragma once

#include <sc-memory/sc_addr.hpp>
#include <sc-memory/sc_object.hpp>

#include "StructureKeynodes.generated.hpp"

namespace weatherForecastStructureModuleNS
{
class StructureKeynodes : public ScObject
{
  SC_CLASS()
  SC_GENERATED_BODY()

public:
  SC_PROPERTY(Keynode("action_fill_weather_forecast_structure"), ForceCreate)
  static ScAddr action_fill_weather_forecast_structure;
  SC_PROPERTY(Keynode("action_recommend_to_bring_umbrella"), ForceCreate)
  static ScAddr action_recommend_to_bring_umbrella;
  SC_PROPERTY(Keynode("question_initiated"), ForceCreate)
  static ScAddr question_initiated;
};

}  // namespace weatherForecastStructureModuleNS
