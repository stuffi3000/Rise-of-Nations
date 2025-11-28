Includes = {
}

PixelShader =
{
	Samplers =
	{
		MapTexture =
		{
			Index = 0
			MagFilter = "Point"
			MinFilter = "Point"
			MipFilter = "None"
			AddressU = "Clamp"
			AddressV = "Clamp"
		}
	}
}


VertexStruct VS_INPUT
{
	float3 vPosition  : POSITION;
	float2 vTexCoord  : TEXCOORD0;
};

VertexStruct VS_OUTPUT
{
	float4  vPosition : PDX_POSITION;
	float2  vTexCoord : TEXCOORD0;
};


ConstantBuffer( 0, 0 )
{
	float4x4 WorldViewProjectionMatrix;
	float4 Color;
	float vXOffset;	// For textures with more than one frame
};



VertexShader =
{
	MainCode VertexShader
	[[

		VS_OUTPUT main(const VS_INPUT v )
		{
		    VS_OUTPUT Out;
		    Out.vPosition  = mul( WorldViewProjectionMatrix, float4( v.vPosition.xyz, 1 ) );

		    Out.vTexCoord  = v.vTexCoord;
			Out.vTexCoord.x += vXOffset;
		    return Out;
		}


	]]
}

PixelShader =
{
	MainCode PixelShaderDefault
	[[

		float4 main( VS_OUTPUT v ) : PDX_COLOR
		{
			return tex2D( MapTexture, v.vTexCoord ) * Color;
		}

	]]

	MainCode PixelShaderOver
	[[

		float4 main( VS_OUTPUT v ) : PDX_COLOR
		{
		    float4 OutColor = tex2D( MapTexture, v.vTexCoord );
		    float4 MixColor = float4( 0.1, 0.1, 0.1, 0 );
		    OutColor += MixColor;
			OutColor *= Color;
		    return OutColor;
		}

	]]
}


BlendState BlendState
{
	BlendEnable = yes
	AlphaTest = no
	SourceBlend = "src_alpha"
	DestBlend = "inv_src_alpha"
}


Effect Up
{
	VertexShader = "VertexShader"
	PixelShader = "PixelShaderDefault"
}

Effect Down
{
	VertexShader = "VertexShader"
	PixelShader = "PixelShaderDefault"
}

Effect Disable
{
	VertexShader = "VertexShader"
	PixelShader = "PixelShaderDefault"
}

Effect Over
{
	VertexShader = "VertexShader"
	PixelShader = "PixelShaderOver"
}

