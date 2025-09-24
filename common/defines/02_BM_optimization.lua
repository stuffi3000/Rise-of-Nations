--------------------------------------------------------------------------------------------------------------
-- BM Optimization Defines
--------------------------------------------------------------------------------------------------------------

Nlua = {
	NTopbar = {
		GAME_SPEED_LIMIT = 0,	-- Unlocks Speed to match as much as the proccessor can handle
		GAME_SPEED_STEPS = 5,	-- DONT CHANGE -- Deals with graphics and speed settings
		GAME_SPEED_ONE = 1,	-- DONT CHANGE --
		GAME_SPEED_TWO = 2,	-- DONT CHANGE --
		GAME_SPEED_THREE = 3,	-- DONT CHANGE --
		GAME_SPEED_FOUR = 4,	-- DONT CHANGE --
		GAME_SPEED_FIVE = 5,	-- DONT CHANGE --
	}
}

NDefines.NGame.LAG_DAYS_FOR_LOWER_SPEED = 15					-- Days of client lag for decrease of gamespeed
NDefines.NGame.LAG_DAYS_FOR_PAUSE = 30						-- Days of client lag for pause of gamespeed.
NDefines.NGame.GAME_SPEED_SECONDS = { 0.15, 0.10, 0.05, 0.005, 0.0 } -- game speeds for each level. Must be 5 entries with last one 0 for unbound

NDefines.NGame.COMBAT_LOG_MAX_MONTHS = 24
NDefines.NFocus.MAX_SAVED_FOCUS_PROGRESS = 30
NDefines.NAI.EQUIPMENT_MARKET_BASE_MARKET_RATIO = 0.35
NDefines.NCountry.EVENT_PROCESS_OFFSET = 30 -- Performance enhancer. --TW/WTT

NDefines.NGame.GAME_SPEED_SECONDS = { 2.0, 0.5, 0.2, 0.05, 0.0 }
NDefines.NGame.MESSAGE_TIMEOUT_DAYS = 14					     	    -- WAS 60 | less messages lying around at the top of your screen

NDefines.NCountry.INTERPOLATED_FRONT_STEPS_SHORT = 1					-- Performance optimization - The amount of steps for interpolated fronts. Non-AI countries got full interpolated fronts, the rest has optimized version of it.