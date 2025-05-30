#include <cstdlib>
#include <ctime>
#include <filesystem>
#include <sys/stat.h>
#include <sc-agents-common/utils/IteratorUtils.hpp>
#include <sc-agents-common/utils/AgentUtils.hpp>
#include "factory/InferenceManagerFactory.hpp"
#include "WeatherRecommendationAgent.hpp"

using namespace std;
using namespace utils;
using namespace inference;

namespace weatherForecastStructureModuleNS
{
    SC_AGENT_IMPLEMENTATION(WeatherRecommendationAgent)
    {
        if (!m_memoryCtx.HelperCheckEdge(StructureKeynodes::action_recommend_to_bring_umbrella, otherAddr, ScType::EdgeAccessConstPosPerm))
            return SC_RESULT_OK;
        SC_LOG_DEBUG("Hypotenuse: started");
        SC_LOG_INFO("WeatherRecommendationAgent: started");

        ScAddr const &keynode_rrel_1 = m_memoryCtx.HelperFindBySystemIdtf("rrel_1");
        ScAddr inputStructure = IteratorUtils::getAnyByOutRelation(&m_memoryCtx, otherAddr, keynode_rrel_1);
        ScAddr const &keynode_rrel_2 = m_memoryCtx.HelperFindBySystemIdtf("rrel_2");
        ScAddr ruleset = IteratorUtils::getAnyByOutRelation(&m_memoryCtx, otherAddr, keynode_rrel_2);
        ScAddr outputStructure = m_memoryCtx.HelperFindBySystemIdtf("output_structure");
        

        InferenceParams const &inferenceParams{ruleset, {}, {inputStructure}, outputStructure};
        InferenceConfig const &inferenceConfig{
            GENERATE_UNIQUE_FORMULAS, REPLACEMENTS_ALL,
            TREE_ONLY_OUTPUT_STRUCTURE,
            SEARCH_IN_STRUCTURES};
        SC_LOG_DEBUG("2");

        std::unique_ptr<InferenceManagerAbstract> inferenceManager = InferenceManagerFactory::constructDirectInferenceManagerAll(&m_memoryCtx, inferenceConfig);
        SC_LOG_DEBUG("3");

        bool targetAchieved = inferenceManager->applyInference(inferenceParams);
        SC_LOG_DEBUG("4");

        inferenceManager->getSolutionTreeManager()->createSolution(outputStructure, targetAchieved);
        SC_LOG_DEBUG("5");

    
        SC_LOG_INFO("WeatherRecommendationAgent: finished");
        utils::AgentUtils::finishAgentWork(&m_memoryCtx, otherAddr, true);
        return SC_RESULT_OK;
    }
}