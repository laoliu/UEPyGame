// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "Logging/LogMacros.h"
#include "Delegates/DelegateCombinations.h"
#include "Misc/StringBuilder.h"
#include "Interfaces/IHttpRequest.h"
#include "ChatGptUtil.generated.h"

DECLARE_LOG_CATEGORY_EXTERN(ChatGpt, Log, All);
DECLARE_DYNAMIC_DELEGATE_OneParam(FChatCallback, FString, ChatMessage);

class FChatSession
{
public:
	int32 LastProcessBytes = 0;  //上一次已经接收处理告知调用方的索引
	FStringBuilderBase MessageStringBuilder;
};

UCLASS()
class UEGENAIPLUGIN_API UChatGptUtil : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

	UFUNCTION(BlueprintCallable, Category = "ChatGpt")
	static void Chat(FString Message, FString Key, FChatCallback ChatCallback);

private:
	static FString ParseCompletionText(FString DataJson);

private:
	static TMap<IHttpRequest*, TSharedRef<FChatSession>> ChatSessions;
};