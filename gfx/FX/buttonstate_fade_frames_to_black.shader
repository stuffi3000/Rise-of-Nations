Includes = {
	"buttonstate.fxh"
	"fade_frames_to_black_constants.fxh"
}

PixelShader =
{
	Samplers =
	{
		MapTexture =
		{
			Index = 0
			MagFilter = "linear"
			MinFilter = "linear"
			MipFilter = "None"
			AddressU = "Wrap"
			AddressV = "Clamp"
		}
	}
}


VertexStruct VS_OUTPUT
{
	float4  vPosition : PDX_POSITION;
	float2  vTexCoord : TEXCOORD0;
};


VertexShader =
{
	MainCode VertexShader
	[[
		VS_OUTPUT main(const VS_INPUT v )
		{
			VS_OUTPUT Out;
			Out.vPosition  = mul( WorldViewProjectionMatrix, float4( v.vPosition.xyz, 1 ) );

			Out.vTexCoord = v.vTexCoord;
			Out.vTexCoord += Offset;
			return Out;
		}
	]]
}

PixelShader =
{
	MainCode PixelShaderUp
	[[
		float4 main( VS_OUTPUT v ) : PDX_COLOR
		{
			float4 OutColor = tex2D( MapTexture, v.vTexCoord );
			OutColor *= min( AnimationTime / FADE_IN_DURATION, 1.0) * min( ( 1.0 - AnimationTime ) / FADE_OUT_DURATION, 1.0);
			OutColor *= Color;
			return OutColor;
		}
	]]

	MainCode PixelShaderDown
	[[
		float4 main( VS_OUTPUT v ) : PDX_COLOR
		{
			float4 OutColor = tex2D( MapTexture, v.vTexCoord );
			OutColor *= min( AnimationTime / FADE_IN_DURATION, 1.0) * min( ( 1.0 - AnimationTime ) / FADE_OUT_DURATION, 1.0);

			float4 MixColor = float4( 0.15, 0.15, 0.15, 0 );
			OutColor.rgb -= ( 0.5 + OutColor.rgb ) * MixColor.rgb;
			return OutColor;
		}
	]]

	MainCode PixelShaderDisable
	[[
		float4 main( VS_OUTPUT v ) : PDX_COLOR
		{
			float4 OutColor = tex2D( MapTexture, v.vTexCoord );
			OutColor *= min( AnimationTime / FADE_IN_DURATION, 1.0) * min( ( 1.0 - AnimationTime ) / FADE_OUT_DURATION, 1.0);

			float Grey = dot( OutColor.rgb, float3( 0.212671f, 0.715160f, 0.072169f ) );
			OutColor.rgb = float3(Grey, Grey, Grey);
			OutColor *= Color;
			return OutColor;
		}
	]]

	MainCode PixelShaderOver
	[[
		float4 main( VS_OUTPUT v ) : PDX_COLOR
		{
			float4 OutColor = tex2D( MapTexture, v.vTexCoord );
			OutColor *= min( AnimationTime / FADE_IN_DURATION, 1.0) * min( ( 1.0 - AnimationTime ) / FADE_OUT_DURATION, 1.0);

			float4 MixColor = float4( 0.15, 0.15, 0.15, 0 );
			OutColor.rgb += ( 0.5 + OutColor.rgb ) * MixColor.rgb;
			return OutColor;
		}
	]]
}


BlendState BlendState
{
	BlendEnable = yes
	SourceBlend = "src_alpha"
	DestBlend = "inv_src_alpha"
}


Effect Up
{
	VertexShader = "VertexShader"
	PixelShader = "PixelShaderUp"
}

Effect Down
{
	VertexShader = "VertexShader"
	PixelShader = "PixelShaderDown"
}

Effect Disable
{
	VertexShader = "VertexShader"
	PixelShader = "PixelShaderDisable"
}

Effect Over
{
	VertexShader = "VertexShader"
	PixelShader = "PixelShaderOver"
}

