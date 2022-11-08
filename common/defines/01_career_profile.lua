NDefines_CareerProfile = {

NCareerProfile = {
	-- Mod defines
	MOD_STATISTICS_GROUP = "", -- Can be set by mods to collect statistics in a separate data set for the mod. Will also be used as the display name if MOD_STATISTICS_GROUP_NAME is not set.
	MOD_STATISTICS_GROUP_NAME = "", -- Can be set by mods as a display name for the mod's statistics data set. It can be a localized.

	-- Statistics parameters
	NAVAL_INVASION_MEDAL_MAX_DURATION = 96, -- Maximum duration in hours to finish naval invasion and get a Naval Invasion Medal
	PARADROP_AWARD_DIVISION_MIN_BATTALION_COUNT = 5, -- Minimum count of battalions in the division required to count that division for paradrop awards ("Paradrop Medal" and "They came from Above")
	NAVAL_INVASION_MEDAL_DIVISION_MIN_BATTALION_COUNT = 5, -- Minimum count of battalions in the division required to count that division for Naval Invasion Medal
	TURNING_TIDE_MEDAL_DIVISION_MIN_BATTALION_COUNT = 5, -- Minimum count of battalions in the division required to count that division for Turning the Tide Medal
	LORD_OF_THE_SEAS_MEDAL_MIN_SUPREMACY = 0.75, -- Minimum supremacy to count current naval region for Lord of the Seas Medal
},

NCareerProfileGUI = {
	AWARD_POPUP_DURATION = 8000, -- Show an award popup for this many milliseconds
	AWARD_POPUP_CONTENT_DELAY = 400, -- Show the content of the award popup after this many milliseconds

	CAREER_POINTS_ANIMATION_DELAY = 950, -- Delay the career points count-up animation by this many milliseconds
	CAREER_POINTS_ANIMATION_DURATION = 950, -- Count the career points up for this many milliseconds
},

}

for k,v in pairs( NDefines_CareerProfile ) do NDefines[k] = v end