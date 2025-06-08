// Copyright Epic Games, Inc. All Rights Reserved.

using UnrealBuildTool;

public class UEGenAIPlugin : ModuleRules
{
	public UEGenAIPlugin(ReadOnlyTargetRules Target) : base(Target)
	{
		PrivateDependencyModuleNames.AddRange(new string[] { "GenerativeAISupport" });
		PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

		PublicDependencyModuleNames.AddRange(new string[] { "Core", "CoreUObject", "Engine", "InputCore", "EnhancedInput","Json", "HTTP" });
	}
}
