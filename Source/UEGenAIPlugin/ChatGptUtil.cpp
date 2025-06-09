// Fill out your copyright notice in the Description page of Project Settings.


#include "ChatGptUtil.h"
#include "HttpModule.h"
#include "Interfaces/IHttpResponse.h"
#include "Dom/JsonObject.h"
#include "Templates/SharedPointer.h"

DEFINE_LOG_CATEGORY(ChatGpt);

#define MESSAGE_BLOCK_SIZE 50

TMap<IHttpRequest*, TSharedRef<FChatSession>> UChatGptUtil::ChatSessions;

void UChatGptUtil::Chat(FString MessageContent, FString Key, FChatCallback ChatCallback)
{
    UE_LOG(ChatGpt, Display, TEXT("chat request: %s"), *MessageContent);

    // 构造请求Json对象
    TSharedPtr<FJsonObject> JsonObject = MakeShareable(new FJsonObject());
    JsonObject->SetStringField(TEXT("model"), TEXT("gpt-4o-2024-08-06"));    
    JsonObject->SetNumberField(TEXT("max_tokens"), 1000);
    JsonObject->SetBoolField(TEXT("stream"), true);  // 流式接收

    TSharedPtr<FJsonObject> Message = MakeShareable(new FJsonObject());
    Message->SetStringField(TEXT("role"), TEXT("user"));
    Message->SetStringField(TEXT("content"), *MessageContent);
    TArray<TSharedPtr<FJsonValue>> Messages;
    Messages.Add(MakeShareable(new FJsonValueObject(Message)));
    JsonObject->SetArrayField(TEXT("messages"), Messages);

    // Json对象序列号成字符串
    FString OutputString;
    TSharedRef<TJsonWriter<TCHAR>> JsonWriter = TJsonWriterFactory<>::Create(&OutputString);
    FJsonSerializer::Serialize(JsonObject.ToSharedRef(), JsonWriter);   
 
    // 发起HTTP请求
    TSharedRef<IHttpRequest> HttpRequest = FHttpModule::Get().CreateRequest();
    HttpRequest->SetVerb("POST");
    HttpRequest->SetHeader("Content-Type", "application/json");
    HttpRequest->SetHeader("Authorization", FString("Bearer ") + Key);
    HttpRequest->SetURL(TEXT("https://ai-gateway.sdpsg.101.com/v1/chat/completions"));
    HttpRequest->SetContentAsString(OutputString);
    HttpRequest->SetTimeout(120);
    // 流式接收在请求进度回调代理处理，非流式接收在请求完成回调代理处理
    HttpRequest->OnRequestProgress64().BindLambda([ChatCallback](FHttpRequestPtr Request, int32 BytesSent, int32 BytesReceived)
        {
            const FHttpResponsePtr Response = Request->GetResponse();
            if (!Response.IsValid())
            {
                return;
            }

            // 本接口支持同时调用，每个请求分配一个对应的状态数据
            TSharedRef<FChatSession>& ChatSession = ChatSessions.FindOrAdd(Request.Get(), TSharedRef<FChatSession>(new FChatSession()));
            FString Content = Response->GetContentAsString();
            if (ChatSession->LastProcessBytes >= Content.Len())
            {
                return;
            }

            FString NewData = Content.Mid(ChatSession->LastProcessBytes, Content.Len() - ChatSession->LastProcessBytes);
            /**
            data: {"id":"chatcmpl-6sM6pSuVMU1ClZujzUs8PvJAFtc11","object":"chat.completion.chunk","created":1678412719,"model":"gpt-3.5-turbo-0301","choices":[{"delta":{"content":"合"},"index":0,"finish_reason":null}]}
            data: [DONE]
            */
            const FString DataToken = TEXT("data: ");
            const FString DoneToken = TEXT("[DONE]");
            bool bDone = false;
            int32 DataTokenIndex = 0;
            int32 NextDataTokenIndex = 0;
            do
            {
                DataTokenIndex = NextDataTokenIndex;
                NextDataTokenIndex = NewData.Find(DataToken, ESearchCase::CaseSensitive, ESearchDir::FromStart, DataTokenIndex+DataToken.Len());

                FString DataJson;
                if (NextDataTokenIndex == -1)  // not found
                {
                    DataJson = NewData.Right(NewData.Len() - DataTokenIndex - DataToken.Len());
                }
                else
                {
                    DataJson = NewData.Mid(DataTokenIndex+DataToken.Len(), NextDataTokenIndex - DataTokenIndex - DataToken.Len());
                }
                
                if (DataJson.Find(DoneToken) != -1)
                {
                    bDone = true;
                    break;
                }
                else
                {
                    FString Text = ParseCompletionText(DataJson);
                    ChatSession->MessageStringBuilder.Append(*Text, Text.Len());
                }
            } while (NextDataTokenIndex != -1);

            FString Message = ChatSession->MessageStringBuilder.ToString();
            if (bDone)
            {                
                if (!Message.IsEmpty())
                {
                    UE_LOG(ChatGpt, Display, TEXT("chat response: %s"), *Message);
                    ChatCallback.Execute(Message);
                }                
                UE_LOG(ChatGpt, Display, TEXT("chat response: done"));
            }
            else
            {                
                ChatSession->LastProcessBytes = Content.Len();
                if (Message.Len() >= MESSAGE_BLOCK_SIZE)
                {                    
                    UE_LOG(ChatGpt, Display, TEXT("chat response: %s"), *Message);
                    ChatCallback.Execute(Message);
                    ChatSession->MessageStringBuilder.Reset();
                }
            }
        });
    HttpRequest->OnProcessRequestComplete().BindLambda([ChatCallback](FHttpRequestPtr Request, FHttpResponsePtr Response,
        bool bWasSuccessful)
        {                    
            ChatSessions.Remove(Request.Get());

            // 请求发送失败
            if (!bWasSuccessful)
            {
                UE_LOG(ChatGpt, Error, TEXT("failed to send the chat request"));
                ChatCallback.Execute("");
                return;
            }

            // 请求成功，但是服务端有报错
            if (Response->GetContentType().Find(TEXT("application/json")) == 0)
            {
                TSharedPtr<FJsonObject> ResponseJsonObject = MakeShareable(new FJsonObject());
                FString Content = Response->GetContentAsString();
                TSharedRef<TJsonReader<TCHAR>> JsonReader = TJsonReaderFactory<TCHAR>::Create(Content);
                FJsonSerializer::Deserialize(JsonReader, ResponseJsonObject);

                const TSharedPtr<FJsonObject>* ErrorJsonObject = nullptr;
                if (ResponseJsonObject->TryGetObjectField(TEXT("error"), ErrorJsonObject))
                {
                    FString Message = (*ErrorJsonObject)->GetStringField(TEXT("message"));
                    UE_LOG(ChatGpt, Error, TEXT("error message: %s"), *Message);
                    ChatCallback.Execute("");
                    return;
                }
            }

            UE_LOG(ChatGpt, Display, TEXT("successful to send the chat request"));
        });
    //FHttpModule::Get().SetProxyAddress(TEXT("http://127.0.0.1:1080"));
    HttpRequest->ProcessRequest();
}

FString UChatGptUtil::ParseCompletionText(FString DataJson)
{
    TSharedPtr<FJsonObject> DataJsonObject = MakeShareable(new FJsonObject());
    TSharedRef<TJsonReader<TCHAR>> JsonReader = TJsonReaderFactory<TCHAR>::Create(DataJson);
    FJsonSerializer::Deserialize(JsonReader, DataJsonObject);

    const TArray< TSharedPtr<FJsonValue> >* Choices = nullptr;
    if (DataJsonObject->TryGetArrayField(TEXT("choices"), Choices))
    {
        if (Choices->Num() > 0)
        {
            TSharedPtr<FJsonObject>ChoiceObject = (*Choices->begin())->AsObject();
            const TSharedPtr<FJsonObject>* DeltaObject = nullptr;
            if (ChoiceObject->TryGetObjectField(TEXT("delta"), DeltaObject))
            {
                FString Text;
                if ((*DeltaObject)->TryGetStringField(TEXT("content"), Text))
                {
                    // GPT3返回的汉字是经过转义的，如\u7943，需要转义回来
                    Text = Text.Replace(TEXT("\n"), TEXT(" ")).ReplaceEscapedCharWithChar();
                    return Text;
                }
            }
        }
    }

    return TEXT("");
}