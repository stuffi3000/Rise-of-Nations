Includes = {
}

PixelShader =
{
	Samplers =
	{
		FrontTexture =
		{
			Index = 0
			MagFilter = "Point"
			MinFilter = "Point"
			MipFilter = "None"
			AddressU = "Wrap"
			AddressV = "Wrap"
		}

		BackTexture =
		{
			Index = 1
			MagFilter = "Point"
			MinFilter = "Point"
			MipFilter = "None"
			AddressU = "Wrap"
			AddressV = "Wrap"
		}
	}
}

VertexStruct VS_INPUT
{
    float4 Position : POSITION;
    float2 TexCoord : TEXCOORD0;
};

VertexStruct VS_OUTPUT
{
    float4 Position : PDX_POSITION;
    float2 TexCoord0 : TEXCOORD0;
};

ConstantBuffer( 0, 0 )
{
	float4x4 WorldViewProjectionMatrix; 
	float4 FrontColor;
	float4 BackColor;
	float CurrentState;
};

VertexShader =
{
	MainCode VertexShader
	[[
		VS_OUTPUT main( const VS_INPUT Input )
		{
			VS_OUTPUT Output;
		   	Output.Position = mul( WorldViewProjectionMatrix, Input.Position );
			Output.TexCoord0 = Input.TexCoord;
			Output.TexCoord0.y = -Output.TexCoord0.y;
			return Output;
		}
	]]
}

PixelShader =
{
	MainCode PixelColor
	[[
		float4 main( VS_OUTPUT Input ) : PDX_COLOR
		{
			if( Input.TexCoord0.x <= .5f && Input.TexCoord0.x <= CurrentState ||
				Input.TexCoord0.x >= .5f && Input.TexCoord0.x >= CurrentState )
			{
				return FrontColor;
			}
			else
			{
				return BackColor;
			}
		}
	]]

	MainCode PixelTexture
	[[
		float4 main( VS_OUTPUT Input ) : PDX_COLOR
		{
			if( Input.TexCoord0.x < .5f && Input.TexCoord0.x >= CurrentState ||
				Input.TexCoord0.x >= .5f && Input.TexCoord0.x <= CurrentState )
			{
				return tex2D( FrontTexture, Input.TexCoord0.xy );
			}
			else
			{
				return tex2D( BackTexture, Input.TexCoord0.xy );
			}
		}
	]]
}

BlendState BlendState
{
	BlendEnable = yes
	SourceBlend = "SRC_ALPHA"
	DestBlend = "INV_SRC_ALPHA"
}

Effect Color
{
	VertexShader = "VertexShader"
	PixelShader = "PixelColor"
}

Effect Texture
{
	VertexShader = "VertexShader"
	PixelShader = "PixelTexture"
}
