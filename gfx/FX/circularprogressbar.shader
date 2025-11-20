Includes = {
}

PixelShader =
{
	Samplers =
	{
		TextureOne =
		{
			Index = 0
			MagFilter = "Linear"
			MinFilter = "Linear"
			MipFilter = "None"
			AddressU = "Wrap"
			AddressV = "Wrap"
		}
		TextureTwo =
		{
			Index = 1
			MagFilter = "Linear"
			MinFilter = "Linear"
			MipFilter = "None"
			AddressU = "Wrap"
			AddressV = "Wrap"
		}
	}
}

VertexStruct VS_INPUT
{
    float2 vPosition  : POSITION;
 	float2 vTexCoord0 : TEXCOORD0;
	float2 vTextureToRender : TEXCOORD1; 	
};

VertexStruct VS_OUTPUT
{
    float4 vPosition  : PDX_POSITION;
 	float2 vTexCoord0 : TEXCOORD0;
 	float2 vTextureToRender : TEXCOORD1; 	
};

ConstantBuffer( 0, 0 )
{
	float4x4 Mat;
};

VertexShader =
{
	MainCode VertexColor
	[[
		VS_OUTPUT main(const VS_INPUT v )
		{
		    VS_OUTPUT Out;
			float4 vPosition = float4( v.vPosition.x, v.vPosition.y, 0, 1 );
		    Out.vPosition  	 = mul( Mat, vPosition );	
			Out.vTexCoord0	 = v.vTexCoord0;
			Out.vTextureToRender = v.vTextureToRender;

		    return Out;
		}
	]]
}

PixelShader =
{
	MainCode PixelColor
	[[
		float4 main( VS_OUTPUT v ) : PDX_COLOR
		{
			float Scale = 0.5;
			float2 TexCoords = (v.vTexCoord0.xy - 0.5) * Scale + (0.5 * Scale);
			TexCoords.y = 1.0 - TexCoords.y;
			float4 Color0 = tex2D( TextureOne, TexCoords - 0.5);
			float4 Color1 = tex2D( TextureTwo, TexCoords - 0.5);
			return lerp( Color0, Color1, v.vTextureToRender.x );
		}
	]]
}

BlendState BlendState
{
	BlendEnable = yes
	SourceBlend = "SRC_ALPHA"
	DestBlend = "INV_SRC_ALPHA"
}

Effect CircularProgressBar
{
	VertexShader = "VertexColor"
	PixelShader = "PixelColor"
}