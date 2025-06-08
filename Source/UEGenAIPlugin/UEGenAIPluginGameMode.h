// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "UEGenAIPluginGameMode.generated.h"

UCLASS(minimalapi)
class AUEGenAIPluginGameMode : public AGameModeBase
{
	GENERATED_BODY()

public:
	AUEGenAIPluginGameMode();
	void OnChatCompletion(const FString& ResponseContent, const FString& ErrorMessage, bool bSuccess);
};



