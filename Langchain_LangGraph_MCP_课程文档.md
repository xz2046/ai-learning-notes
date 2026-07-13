# 新版 Langchain + LangGraph + MCP 的智能体和工作流开发

**讲师**: 肖斌
**总页数**: 79
**提取时间**: 2026-07-01 18:48:29

---


## 第1页

新 版   Langchain   +   LangGraph  +MCP   的智能体和工作流开发  讲师：肖斌，   今晚   VIP   直播课， 8   点   05   分开始  内容：  1 、第二期直播的内容预告  2 、学习路线的要求  3 、上期的部分同学简历和工作情况汇报  4 、多（全）模态大模型部署   +   应用开发  第一章、大模型选择和私有化部署  强烈建议：在大模型开发中，要熟悉各种顶级的   AI   大模型的使用和微调。包括： gpt-  4o ，   gpt-o1-mini ，   gpt-o3 ， claude-3.5-sonnet ， claude-3.7-sonnet ， gemini-1.5,  deepseek   系列 ,   qwen   系列。  1 、 Deepseek-V3

## 第3页

2 、 Qwen3  4   月   29   日，发布了   Qwen3   系列模型。我们的旗舰模型 **Qwen3-235B-A22B** 在编  码、数学、通用能力等基准测试中，与   DeepSeek-R1 、 o1 、 o3-mini 、 Grok-3   和  Gemini-2.5-Pro   等其他顶级模型相比，取得了极具竞争力的成绩。此外，小型   MoE   模

## 第4页

型 **Qwen3-30B-A3B   的 ** 激活参数量是   QwQ-32B   的   10   倍，即使是像   Qwen3-4B   这  样的微型模型，其性能也能与   Qwen2.5-72B-Instruct   相媲美。  开源的   Qwen3-235B-A22B   是一个大型模型，总参数量达   2350   亿，激活参数量达  220   亿； Qwen3-30B-A3B   是一个较小的   MoE   模型，总参数量达   300   亿，激活参数量  达   30   亿。此外，六个   Dense   模型也已开源，包括   Qwen3-32B   、   Qwen3-14B   、  Qwen3-8B   、   Qwen3-4B   、 Qwen3-1.7B   和   Qwen3-0.6B   ，它们均遵循   Apache   2.0  许可证。  Qwen3   的亮点包括：  •   各种尺寸的密集和混合专家   (MoE)   模型   ，有   0.6B 、 1.7B 、 4B 、 8B 、 14B 、 32B  和   30B-A3B 、 235B-A22B   可供选择。  •   思维模式 （用于复杂的逻辑推理、数学和编码）和   非思维模式   （用于高效、通  用的聊天）之间的无缝切换，确保在各种场景下实现最佳性能。  •   推理能力大幅增强   ，在数学、代码生成、常识逻辑推理等方面超越了之前 的  QwQ （思维模式）和   Qwen2.5   指令模型（非思维模式）。  •   卓越的人类偏好一致性   ，擅长创意写作、角色扮演、多轮对话和指令遵循，提供  更自然、更具吸引力和身临其境的对话体验。  •   精通   Agent   能力   ，能够以思考和非思考两种模式与外部工具精准集成，并增强  了对   MCP   的支持，在基于   Agent   的复杂任务中取得开源模型的领先性能。  •   支持   100   多种语言和方言，支持   119   种语言和方言  3 、私有化部署

## 第5页

显存计算器  •   大模型显存需求分析工具   |   LlamaFactory   |   LlamaFactory:  https://www.llamafactory.cn/tools/gpu-memory-estimation.html  一、下载模型  打开网站： https://www.modelscope.cn/organization/Qwen?tab=collection

## 第6页

Shell  from   modelscope   import   snapshot_download  #   model_dir   =   snapshot_download('ZhipuAI/glm-4-9b-chat',  cache_dir='/root/autodl-tmp/models',   revision='master')  #   model_dir   =   snapshot_download('deepseek-ai/DeepSeek-R1-Distill-  Qwen-7B',   cache_dir='/root/autodl-tmp/models',   revision='master')  #   model_dir   =   snapshot_download('LLM-Research/Meta-Llama-3.1-8B-  Instruct',   cache_dir='/root/autodl-tmp/models',   revision='master')  #   model_dir   =   snapshot_download('Qwen/Qwen2.5-7B-Instruct',  cache_dir='/root/autodl-tmp/models',   revision='master')  # 模型下载  #   from   modelscope   import   snapshot_download  #   model_dir   =   snapshot_download('LLM-Research/Meta-Llama-3.1-8B-  Instruct')  #   model_dir   =   snapshot_download('Qwen/Qwen3-8B',  cache_dir='/root/autodl-tmp/models',   revision='master')  model_dir   =   snapshot_download('Qwen/Qwen2.5-Omni-3B',  cache_dir='/root/autodl-tmp/models',   revision='master')  二、通过   vllm   server   命令部署  企业生产环境中，不要使用   Ollama   部署

## 第7页

以下是   Ollama   和   vLLM   在部署方面的对比表格：  对比维度   Ollama   vLLM  定位   轻量化本地部署工具，适合个人开  发者和快速原型验证  高性能推理框架，面向企业级  生产环境和高并发场景  部署复杂度   低，支持一键安装和运行（如  ollama   run   命令）  中高，需配置   Python   环境、  API   服务接口和分布式集群  硬件要求   支持   CPU/GPU ，最低配置为   16G B  内存（运行   7B   模型）  强制需要   GPU （如   NVIDIA  Tesla   系列），显存要求较高  并发能力   有限，适合单会话或少量并发   支持高并发，通过连续批处理  （ Continuous   Batching ）优化  吞吐量   1  资源占用   单机环境下资源占用低，启动快   资源占用高但利用率优，支持  多机多卡扩展  延迟表现   实时交互场景延迟更低   通过批处理平衡延迟与吞吐，  适合高吞吐场景  生态支持   丰富的预置模型（如   Llama   系   聚焦推理优化，企业级功能丰

## 第8页

列），支持跨平台  （ Windows/macOS/Linux ）  富（如分布式推理、量化支  持）  典型安装命  令  curl   -fsSL  https://ollama.com/install.s  h   |   sh （ Linux ） 1  pip   install   vllm   +   配 置  API   服务  适用场景   快速原型验证、本地开发、教育演  示、资源受限环境  企业级   API   服务、高并发聊天  机器人、多   GPU   集群任务  模型格式支  持  GGUF   格式（适合量化与跨平台）   HuggingFace   Transformer s  格式（ .bin/.safetensors ）  长上下文支  持  默认   4K-8K   tokens   支持   32K-128K   tokens （依 赖  PagedAttention   技术）  量化支持   自动支持   Q4_0 、 Q5_K   等量化格式   需外部工具（ 如  bitsandbytes ）实现量化  vllm   的命令说明  首先需要安装：   pip   install   vllm  OpenAI   兼容服务器   —   vLLM   文档  usage:   vllm   serve   [-h]   [--host   HOST]   [--port   PORT]  [--uvicorn-log-level   {debug,info,warning,error,critical,trace}]  [--disable-uvicorn-access-log]   [--allow-credentials]  [--allowed-origins   ALLOWED_ORIGINS]  [--allowed-methods   ALLOWED_METHODS]  [--allowed-headers   ALLOWED_HEADERS]   [--api-key   API_KEY]  [--lora-modules   LORA_MODULES   [LORA_MODULES   ...]]  [--prompt-adapters   PROMPT_ADAPTERS   [PROMPT_ADAPTERS   ...]]  [--chat-template   CHAT_TEMPLATE]  [--chat-template-content-format   {auto,string,openai}]  [--response-role   RESPONSE_ROLE]   [--ssl-keyfile   SSL_KEYFILE]  [--ssl-certfile   SSL_CERTFILE]   [--ssl-ca-certs   SSL_CA_CERTS]  [--enable-ssl-refresh]   [--ssl-cert-reqs   SSL_CERT_REQS]

## 第9页

[--root-path   ROOT_PATH]   [--middleware   MIDDLEWARE]  [--return-tokens-as-token-ids]  [--disable-frontend-multiprocessing]  [--enable-request-id-headers]   [--enable-auto-tool-choice]  [--tool-call-parser   {granite-20b-  fc,granite,hermes,internlm,jamba,llama3_json,mistral,phi4_mini_json,pythonic}   or  name   registered   in   --tool-parser-plugin]  [--tool-parser-plugin   TOOL_PARSER_PLUGIN]   [--model   MODEL]  [--task   {auto,generate,embedding,embed,classify,score,reward,transcription}]  [--tokenizer   TOKENIZER]   [--hf-config-path   HF_CONFIG_PATH]  [--skip-tokenizer-init]   [--revision   REVISION]  [--code-revision   CODE_REVISION]  [--tokenizer-revision   TOKENIZER_REVISION]  [--tokenizer-mode   {auto,slow,mistral,custom}]  [--trust-remote-code]  [--allowed-local-media-path   ALLOWED_LOCAL_MEDIA_PATH]  [--download-dir   DOWNLOAD_DIR]  [--load-format  {auto,pt,safetensors,npcache,dummy,tensorizer,sharded_state,gguf,bitsandbytes,mis  tral,runai_streamer,fastsafetensors}]  [--config-format   {auto,hf,mistral}]  [--dtype   {auto,half,float16,bfloat16,float,float32}]  [--kv-cache-dtype   {auto,fp8,fp8_e5m2,fp8_e4m3}]  [--max-model-len   MAX_MODEL_LEN]  [--guided-decoding-backend   GUIDED_DECODING_BACKEND]  [--logits-processor-pattern   LOGITS_PROCESSOR_PATTERN]  [--model-impl   {auto,vllm,transformers}]  [--distributed-executor-backend   {ray,mp,uni,external_launcher}]  [--pipeline-parallel-size   PIPELINE_PARALLEL_SIZE]  [--tensor-parallel-size   TENSOR_PARALLEL_SIZE]  [--data-parallel-size   DATA_PARALLEL_SIZE]  [--enable-expert-parallel]  [--max-parallel-loading-workers   MAX_PARALLEL_LOADING_WORKERS]  [--ray-workers-use-nsight]   [--block-size   {8,16,32,64,128}]

## 第10页

[--enable-prefix-caching   |   --no-enable-prefix-caching]  [--prefix-caching-hash-algo   {builtin,sha256}]  [--disable-sliding-window]   [--use-v2-block-manager]  [--num-lookahead-slots   NUM_LOOKAHEAD_SLOTS]   [--seed   SEED]  [--swap-space   SWAP_SPACE]   [--cpu-offload-gb   CPU_OFFLOAD_GB]  [--gpu-memory-utilization   GPU_MEMORY_UTILIZATION]  [--num-gpu-blocks-override   NUM_GPU_BLOCKS_OVERRIDE]  [--max-num-batched-tokens   MAX_NUM_BATCHED_TOKENS]  [--max-num-partial-prefills   MAX_NUM_PARTIAL_PREFILLS]  [--max-long-partial-prefills   MAX_LONG_PARTIAL_PREFILLS]  [--long-prefill-token-threshold   LONG_PREFILL_TOKEN_THRESHOLD]  [--max-num-seqs   MAX_NUM_SEQS]   [--max-logprobs   MAX_LOGPROBS]  [--disable-log-stats]  [--quantization  {aqlm,awq,deepspeedfp,tpu_int8,fp8,ptpc_fp8,fbgemm_fp8,modelopt,nvfp4,marlin,gg  uf,gptq_marlin_24,gptq_marlin,awq_marlin,gptq,compressed-  tensors,bitsandbytes,qqq,hqq,experts_int8,neuron_quant,ipex,quark,moe_wna16,tor  chao,None}]  [--rope-scaling   ROPE_SCALING]   [--rope-theta   ROPE_THETA]  [--hf-token   [HF_TOKEN]]   [--hf-overrides   HF_OVERRIDES]  [--enforce-eager]  [--max-seq-len-to-capture   MAX_SEQ_LEN_TO_CAPTURE]  [--disable-custom-all-reduce]  [--tokenizer-pool-size   TOKENIZER_POOL_SIZE]  [--tokenizer-pool-type   TOKENIZER_POOL_TYPE]  [--tokenizer-pool-extra-config   TOKENIZER_POOL_EXTRA_CONFIG]  [--limit-mm-per-prompt   LIMIT_MM_PER_PROMPT]  [--mm-processor-kwargs   MM_PROCESSOR_KWARGS]  [--disable-mm-preprocessor-cache]   [--enable-lora]  [--enable-lora-bias]   [--max-loras   MAX_LORAS]  [--max-lora-rank   MAX_LORA_RANK]  [--lora-extra-vocab-size   LORA_EXTRA_VOCAB_SIZE]  [--lora-dtype   {auto,float16,bfloat16}]  [--long-lora-scaling-factors   LONG_LORA_SCALING_FACTORS]

## 第11页

[--max-cpu-loras   MAX_CPU_LORAS]   [--fully-sharded-loras]  [--enable-prompt-adapter]  [--max-prompt-adapters   MAX_PROMPT_ADAPTERS]  [--max-prompt-adapter-token   MAX_PROMPT_ADAPTER_TOKEN]  [--device   {auto,cuda,neuron,cpu,tpu,xpu,hpu}]  [--num-scheduler-steps   NUM_SCHEDULER_STEPS]  [--use-tqdm-on-load   |   --no-use-tqdm-on-load]  [--multi-step-stream-outputs   [MULTI_STEP_STREAM_OUTPUTS]]  [--scheduler-delay-factor   SCHEDULER_DELAY_FACTOR]  [--enable-chunked-prefill   [ENABLE_CHUNKED_PREFILL]]  [--speculative-config   SPECULATIVE_CONFIG]  [--model-loader-extra-config   MODEL_LOADER_EXTRA_CONFIG]  [--ignore-patterns   IGNORE_PATTERNS]  [--preemption-mode   PREEMPTION_MODE]  [--served-model-name   SERVED_MODEL_NAME   [SERVED_MODEL_NAME   ...]]  [--qlora-adapter-name-or-path   QLORA_ADAPTER_NAME_OR_PATH]  [--show-hidden-metrics-for-version   SHOW_HIDDEN_METRICS_FOR_VERSION]  [--otlp-traces-endpoint   OTLP_TRACES_ENDPOINT]  [--collect-detailed-traces   COLLECT_DETAILED_TRACES]  [--disable-async-output-proc]  [--scheduling-policy   {fcfs,priority}]  [--scheduler-cls   SCHEDULER_CLS]  [--override-neuron-config   OVERRIDE_NEURON_CONFIG]  [--override-pooler-config   OVERRIDE_POOLER_CONFIG]  [--compilation-config   COMPILATION_CONFIG]  [--kv-transfer-config   KV_TRANSFER_CONFIG]  [--worker-cls   WORKER_CLS]  [--worker-extension-cls   WORKER_EXTENSION_CLS]  [--generation-config   GENERATION_CONFIG]  [--override-generation-config   OVERRIDE_GENERATION_CONFIG]  [--enable-sleep-mode]   [--calculate-kv-scales]  [--additional-config   ADDITIONAL_CONFIG]   [--enable-reasoning]  [--reasoning-parser   {deepseek_r1,granite}]

## 第12页

[--disable-cascade-attn]  [--disable-chunked-mm-input   [DISABLE_CHUNKED_MM_INPUT]]  [--disable-log-requests]   [--max-log-len   MAX_LOG_LEN]  [--disable-fastapi-docs]   [--enable-prompt-tokens-details]  [--enable-server-load-tracking]  命名参数详解  •   --host   主机名。  •   --port   端口号。  默认值： 8000  •   --uvicorn-log-level   可能选项： debug,   info,   warning,   error,   critical,   trace  uvicorn   的日志级别。  默认值： “ info ”  •   --disable-uvicorn-access-log   禁用   uvicorn   访问日志。  默认值： False  •   --allow-credentials   允许凭据。  默认值： False  •   --allowed-origins   允许的来源。  默认值： [ ‘ * ’ ]  •   --allowed-methods   允许的方法。  默认值： [ ‘ * ’ ]  •   --allowed-headers   允许的标头。

## 第13页

默认值： [ ‘ * ’ ]  •   --api-key   如果提供，服务器将要求在标头中提供此密钥。  •   --lora-modules ： LoRA   模块配置，格式为   ‘ name=path ’   或   JSON   格式。示例  （旧格式）： <span   class="pre">'name=path'</span>   示例（新格式）： <span  class="pre">{"name":</span><span>   </span><span  class="pre">"name",</span><span>   </span><span  class="pre">"path":</span><span>   </span><span  class="pre">"lora_path",</span><span>   </span><span  class="pre">"base_model_name":</span><span>   </span><span  class="pre">"id"}</span>  •   --prompt-adapters   提示适配器配置，格式为   name=path 。可以指定多个适配  器。  •   --chat-template   指定模型的聊天模板文件路径或单行形式的模板。  •   --chat-template-content-format   可能选项： auto,   string,   openai  在聊天模板中渲染消息内容的格式。  ￮   “ string ”   将内容渲染为字符串。示例： <span  class="pre">"Hello</span><span>   </span><span  class="pre">World"</span>  ￮   “ openai ”   将内容渲染为字典列表，类似于   OpenAI   模式。示例： <span  class="pre">[{"type":</span><span>   </span><span  class="pre">"text",</span><span>   </span><span  class="pre">"text":</span><span>   </span><span  class="pre">"Hello</span><span>   </span><span  class="pre">world!"}]</span>  默认值： “ auto ”  •   --response-role   如果   <span  class="pre">request.add_generation_prompt=true</span> ，则返回的角色名  称。  默认值： assistant

## 第14页

•   --ssl-keyfileSSL   密钥文件的文件路径。  •   --ssl-certfileSSL   证书文件的文件路径。  •   --ssl-ca-certsCA   证书文件。  •   --enable-ssl-refresh   当   SSL   证书文件更改时刷新   SSL   上下文  默认值： False  •   --ssl-cert-reqs   是否需要客户端证书（请参阅   stdlib   ssl   模块）。  默认值： 0  •   --root-path   当应用程序位于基于路径的路由代理之后时， FastAPI   root_path 。  •   --middleware   要应用于应用程序的其他   ASGI   中间件。我们接受多个   --  middleware   参数。该值应为导入路径。如果提供了函数， vLLM   将使用   <span  class="pre">@app.middleware('http')</span>   将其添加到服务器。如果提供了  类， vLLM   将使用   <span   class="pre">app.add_middleware()</span>   将其添加  到服务器。  默认值： []  •   --return-tokens-as-token-ids   当指定   <span   class="pre">--max-  logprobs</span>   时，将单个   token   表示为   ‘ token_id:{token_id} ’   形式的字符串，以  便可以识别不可   JSON   编码的   token 。  默认值： False  •   --disable-frontend-multiprocessing   如果指定，将在与模型服务引擎相同的进程中  运行   OpenAI   前端服务器。  默认值： False  •   --enable-request-id-headers   如果指定， API   服务器将在响应中添加   X-Request-

## 第15页

Id   标头。注意：在高   QPS   下，这会降低性能。  默认值： False  •   --enable-auto-tool-choice   为支持的模型启用自动工具选择。使用   <span  class="pre">--tool-call-parser</span>   指定要使用的解析器。  默认值： False  •   --tool-call-parser   根据您使用的模型选择工具调用解析器。这用于将模型生成的  工具调用解析为   OpenAI   API   格式。 <span   class="pre">--enable-auto-tool-  choice</span>   需要此参数。  •   --tool-parser-plugin   指定工具解析器插件，用于将模型生成的工具解析为   OpenAI  API   格式，在此插件中注册的名称可在   <span   class="pre">--tool-call-  parser</span>   中使用。  默认值： “”  •   --model   要使用的   huggingface   模型的名称或路径。  默认值： “ facebook/opt-125m ”  •   --task   可能选项： auto,   generate,   embedding,   embed,   classify,   score,   reward,  transcription  模型要执行的任务。即使同一个模型可以用于多个任务，每个   vLLM   实例也仅支持一  个任务。当模型仅支持一个任务时，可以使用   <span   class="pre">"auto"</span>  选择它；否则，您必须明确指定要使用的任务。  默认值： “ auto ”  •   --tokenizer   要使用的   huggingface   分词器的名称或路径。如果未指定，将使用模  型名称或路径。  •   --hf-config-path   要使用的   huggingface   配置的名称或路径。如果未指定，将使用  模型名称或路径。  •   --skip-tokenizer-init   跳过分词器和反分词器的初始化。期望输入中提供有效的

## 第16页

prompt_token_ids ，并且   prompt   为   None 。生成的输出将包含   token   ID 。  默认值： False  •   --revision   要使用的特定模型版本。它可以是分支名称、标签名称或提交   ID 。如  果未指定，将使用默认版本。  •   --code-revision   用于   Hugging   Face   Hub   上模型代码的特定修订版本。它可以是  分支名称、标签名称或提交   ID 。如果未指定，将使用默认版本。  •   --tokenizer-revision   要使用的   huggingface   分词器的修订版本。它可以是分支名  称、标签名称或提交   ID 。如果未指定，将使用默认版本。  •   --tokenizer-mode   可能选项： auto,   slow,   mistral,   custom  分词器模式。  ￮   “ auto ”   将在可用时使用快速分词器。  ￮   “ slow ”   将始终使用慢速分词器。  ￮   “ mistral ”   将始终使用   mistral_common   分词器。  ￮   “ custom ”   将使用   – tokenizer   选择预注册的分词器。  默认值： “ auto ”  •   --trust-remote-code   信任来自   huggingface   的远程代码。  默认值： False  •   --allowed-local-media-path   允许   API   请求从服务器文件系统指定的目录读取本地  图像或视频。这是一个安全风险。仅应在受信任的环境中启用。  •   --download-dir   下载和加载权重的目录。  •   --load-format   可能选项： auto,   pt,   safetensors,   npcache,   dummy,   tensorizer,  sharded_state,   gguf,   bitsandbytes,   mistral,   runai_streamer,   fastsafetensors  要加载的模型权重的格式。

## 第17页

￮   “ auto ”   将尝试加载   safetensors   格式的权重，如果   safetensors   格式不可  用，则回退到   pytorch   bin   格式。  ￮   “ pt ”   将加载   pytorch   bin   格式的权重。  ￮   “ safetensors ”   将加载   safetensors   格式的权重。  ￮   “ npcache ”   将加载   pytorch   格式的权重，并存储   numpy   缓存以加速加载。  ￮   “ dummy ”   将使用随机值初始化权重，主要用于性能分析。  ￮   “ tensorizer ”   将使用   CoreWeave   的   tensorizer   加载权重。有关更多信息，请  参阅 “ 示例 ” 部分中的 “ 张量化   vLLM   模型 ” 脚本。  ￮   “ runai_streamer ”   将使用   Run:ai   Model   Streamer   加载   Safetensors   权重。  ￮   “ bitsandbytes ”   将使用   bitsandbytes   量化加载权重。  ￮   “ sharded_state ”   将从预分片检查点文件加载权重，支持高效加载张量并行  模型  ￮   “ gguf ”   将从   GGUF   格式文件加载权重（详细信息请参阅   ggml-org/ggml ）。  ￮   “ mistral ”   将从   Mistral   模型使用的合并   safetensors   文件加载权重。  默认值： “ auto ”  •   --config-format   可能选项： auto,   hf,   mistral  要加载的模型配置的格式。  ￮   “ auto ”   将尝试加载   hf   格式的配置，如果不可用，则尝试加载   mistral   格式  默认值： “ ConfigFormat.AUTO ”  •   --dtype   可能选项： auto,   half,   float16,   bfloat16,   float,   float32  模型权重和激活的数据类型。  ￮   “ auto ”   将对   FP32   和   FP16   模型使用   FP16   精度，对   BF16   模型使用   BF16  精度。  ￮   “ half ”   表示   FP16 。推荐用于   AWQ   量化。  ￮   “ float16 ”   与   “ half ”   相同。  ￮   “ bfloat16 ”   在精度和范围之间取得平衡。  ￮   “ float ”   是   FP32   精度的简写。  ￮   “ float32 ”   表示   FP32   精度。

## 第18页

默认值： “ auto ”  •   --kv-cache-dtype   可能选项： auto,   fp8,   fp8_e5m2,   fp8_e4m3  kv   缓存存储的数据类型。如果为   “ auto ” ，将使用模型数据类型。 CUDA   11.8+   支持  fp8   (=fp8_e4m3)   和   fp8_e5m2 。 ROCm   (AMD   GPU)   支持   fp8   (=fp8_e4m3)  默认值： “ auto ”  •   --max-model-len   模型上下文长度。如果未指定，将自动从模型配置中派生。支  持   k/m/g/K/M/G   人类可读格式。示例： -   1k   →   1000   -   1K   →   1024  •   --guided-decoding-backend   默认情况下，哪个引擎将用于引导解码（ JSON   模式  / 正则表达式等）。当前支持   mlc-ai/xgrammar   和   guidance-ai/llguidance.Valid 。有效  的后端值包括   “ xgrammar ” 、 “ guidance ”   和   “ auto ” 。使用   “ auto ”   时，我们将根据请求内  容和后端库当前支持的内容做出有主见的决定，因此行为可能会在每个版本中更改。  默认值： “ xgrammar ”  •   --logits-processor-pattern   可选的正则表达式模式，用于指定可以使用  logits_processors   额外完成参数传递的有效   logits   处理器限定名称。默认为   None ，表  示不允许任何处理器。  •   --model-impl   可能选项： auto,   vllm,   transformers  要使用的模型实现。  ￮   “ auto ”   将尝试使用   vLLM   实现（如果存在），如果   vLLM   实现不可用，则回  退到   Transformers   实现。  ￮   “ vllm ”   将使用   vLLM   模型实现。  ￮   “ transformers ”   将使用   Transformers   模型实现。  默认值： “ auto ”  •   --distributed-executor-backend   可能选项： ray,   mp,   uni,   external_launcher  用于分布式模型工作程序的后端，可以是   “ ray ”   或   “ mp ” （多进程）。如果  pipeline_parallel_size   和   tensor_parallel_size   的乘积小于或等于可用   GPU   的数量，  “ mp ”   将用于保持在单个主机上处理。否则，如果安装了   Ray ，则默认为   “ ray ” ，否则将

## 第19页

失败。请注意， tpu   仅支持   Ray   进行分布式推理。  •   --pipeline-parallel-size,   -pp   流水线并行阶段数。  默认值： 1  •   --tensor-parallel-size,   -tp   张量并行副本数。  默认值： 1  •   --data-parallel-size,   -dp   数据并行副本数。 MoE   层将根据   tensor-parallel-size   和  data-parallel-size   的乘积进行分片。  默认值： 1  •   --enable-expert-parallel   对   MoE   层使用专家并行而不是张量并行。  默认值： False  •   --max-parallel-loading-workers   在多个批次中顺序加载模型，以避免在使用张量  并行和大型模型时出现   RAM   OOM 。  •   --ray-workers-use-nsight   如果指定，则使用   nsight   分析   Ray   工作程序。  默认值： False  •   --block-size   可能选项： 8,   16,   32,   64,   128  token   块大小，用于   token   的连续块。在   neuron   设备上将被忽略，并设置为   <span  class="pre">--max-model-len</span> 。在   CUDA   设备上，仅支持最大为   32   的  块大小。在   HPU   设备上，块大小默认为   128 。  •   --enable-prefix-caching,   --no-enable-prefix-caching   启用自动前缀缓存。使用  <span   class="pre">--no-enable-prefix-caching</span>   显式禁用。  •   --prefix-caching-hash-algo   可能选项： builtin,   sha256  设置前缀缓存的哈希算法。选项包括   ‘ builtin ’ （ Python   的内置哈希）或   ‘ sha256 ’ （抗冲  突但具有一定开销）。

## 第20页

默认值： “ builtin ”  •   --disable-sliding-window   禁用滑动窗口，限制为滑动窗口大小。  默认值： False  •   --use-v2-block-manager[ 已弃用 ]   块管理器   v1   已被删除，  SelfAttnBlockSpaceManager （即块管理器   v2 ）现在是默认设置。将此标志设置为  True   或   False   对   vLLM   行为没有影响。  默认值： True  •   --num-lookahead-slots   推测解码所需的实验性调度配置。这将在未来被推测配置  取代；它目前的存在是为了启用正确性测试。  默认值： 0  •   --seed   操作的随机种子。  •   --swap-space   每个   GPU   的   CPU   交换空间大小   (GiB) 。  默认值： 4  •   --cpu-offload-gb   每个   GPU   要卸载到   CPU   的空间，以   GiB   为单位。默认值为  0 ，表示不卸载。直观地看，此参数可以看作是增加   GPU   内存大小的虚拟方法。例  如，如果您有一个   24   GB   GPU   并将其设置为   10 ，则实际上可以将其视为   34   GB  GPU 。然后，您可以加载一个   13B   模型和   BF16   权重，这至少需要   26GB   GPU   内  存。请注意，这需要快速的   CPU-GPU   互连，因为模型的一部分在每次模型前向传递  中都会从   CPU   内存动态加载到   GPU   内存。  默认值： 0  •   --gpu-memory-utilization   用于模型执行器的   GPU   内存的比例，范围为   0   到   1 。  例如，值为   0.5   表示   50%   的   GPU   内存利用率。如果未指定，将使用默认值   0.9 。这  是一个按实例限制，仅适用于当前的   vLLM   实例。如果您在同一   GPU   上运行另一个  vLLM   实例，则无关紧要。例如，如果您在同一   GPU   上运行两个   vLLM   实例，则可以  将每个实例的   GPU   内存利用率设置为   0.5 。  默认值： 0.9

## 第21页

•   --num-gpu-blocks-override   如果指定，则忽略   GPU   性能分析结果，并使用此  GPU   块数。用于测试抢占。  •   --max-num-batched-tokens   每次迭代的最大批处理   token   数。  •   --max-num-partial-prefills   对于分块预填充，最大并发部分预填充数。  默认值： 1  •   --max-long-partial-prefills   对于分块预填充，将并发预填充的最大提示数（提示长  度超过   – long-prefill-token-threshold ）。将此值设置得小于   – max-num-partial-prefills  将允许较短的提示在某些情况下跳过较长提示的队列，从而提高延迟。  默认值： 1  •   --long-prefill-token-threshold   对于分块预填充，如果提示长度超过此   token   数，  则该请求被认为是长的。  默认值： 0  •   --max-num-seqs   每次迭代的最大序列数。  •   --max-logprobs   要返回的最大对数概率数， logprobs   在   SamplingParams   中指  定。  默认值： 20  •   --disable-log-stats   禁用日志统计信息。  默认值： False  •   --quantization,   -q   可选选项： aqlm,   awq,   deepspeedfp,   tpu_int8,   fp8,   ptpc_fp8,  fbgemm_fp8,   modelopt,   nvfp4,   marlin,   gguf,   gptq_marlin_24,   gptq_marlin,  awq_marlin,   gptq,   compressed-tensors,   bitsandbytes,   qqq,   hqq,   experts_int8,  neuron_quant,   ipex,   quark,   moe_wna16,   torchao,   None  用于量化权重的技术。如果为   None ，我们首先检查模型配置文件中的  quantization_config   属性。如果该属性也为   None ，我们则假定模型权重未被量化，并

## 第22页

使用   dtype   来确定权重的   data   type （数据类型）。  •   --rope-scalingRoPE   scaling （ RoPE   缩放）配置， JSON   格式。例如： <span  class="pre">{"rope_type":"dynamic","factor":2.0}</span>  •   --rope-thetaRoPE   theta 。与   rope_scaling   配合使用。在某些情况下，更改   RoPE  theta   可以提高缩放模型的性能。  •   --hf-token   用作远程文件   HTTP   bearer   authorization （持有者授权）的   token （令  牌）。如果为   True ，将使用运行   huggingface-cli   login   时生成的   token （存储在  ~/.huggingface   中）。  •   --hf-overridesHuggingFace   配置的额外参数。这应该是一个   JSON   字符串，将被  解析为一个字典。  •   --enforce-eager   始终使用   eager-mode （ eager   模式）   PyTorch 。如果为   False ，  将结合使用   eager   mode   和   CUDA   graph （ CUDA   图）以获得最大的性能和灵活性。  默认值： False  •   --max-seq-len-to-captureCUDA   graphs （ CUDA   图）覆盖的最大序列长度。当序  列的上下文长度大于此值时，我们将回退到   eager   mode （ eager   模式）。此外，对于  encoder-decoder （编码器 - 解码器）模型，如果   encoder   input （编码器输入）的序列  长度大于此值，我们也将回退到   eager   mode （ eager   模式）。  默认值： 8192  •   --disable-custom-all-reduce   请参阅   ParallelConfig 。  默认值： False  --tokenizer-pool-size   用于异步   tokenization （分词）的   tokenizer   pool （分词器池）的  大小。如果为   0 ，将使用同步   tokenization （分词）。  默认值： 0

## 第23页

--tokenizer-pool-type   用于异步   tokenization （分词）的   tokenizer   pool （分词器池）的  类型。如果   tokenizer_pool_size   为   0 ，则忽略此项。  默认值： “ ray ”  --tokenizer-pool-extra-configtokenizer   pool （分词器池）的额外配置。这应该是一个  JSON   字符串，将被解析为一个字典。如果   tokenizer_pool_size   为   0 ，则忽略此项。  --limit-mm-per-prompt   对于每个   multimodal   plugin （多模态插件），限制每个   prompt  （提示）允许的输入实例数量。期望一个逗号分隔的项目列表，例如：  image=16,video=2   允许每个   prompt （提示）最多   16   张图像和   2   个视频。默认为每种  模态   1 。  --mm-processor-kwargs   多模态输入映射 / 处理的覆盖设置，例如，图像处理器。例  如： <span   class="pre">{"num_crops":</span><span>   </span><span  class="pre">4}</span> 。  --disable-mm-preprocessor-cache   如果为   true ，则禁用   multi-modal  preprocessor/mapper （多模态预处理器 / 映射器）的缓存。（不推荐）  默认值： False  --enable-lora   如果为   True ，启用   LoRA   adapters （ LoRA   适配器）的处理。  默认值： False  --enable-lora-bias   如果为   True ，为   LoRA   adapters （ LoRA   适配器）启用   bias （偏  置）。  默认值： False  --max-loras   单个   batch （批次）中   LoRA   的最大数量。

## 第24页

默认值： 1  --max-lora-rankLoRA   rank （ LoRA   秩）的最大值。  默认值： 16  --lora-extra-vocab-sizeLoRA   adapter （ LoRA   适配器）中可能存在的额外   vocabulary  （词汇表）的最大大小（添加到基础模型   vocabulary （词汇表））。  默认值： 256  --lora-dtype   可选选项： auto,   float16,   bfloat16  LoRA   的   data   type （数据类型）。如果为   auto ，将默认为基础模型   dtype 。  默认值： “ auto ”  --long-lora-scaling-factors   指定多个   scaling   factors （缩放因子）（可以与基础模型  scaling   factor   不同   -   请参阅例如   Long   LoRA ），以允许同时使用使用这些   scaling  factors   训练的多个   LoRA   adapters （ LoRA   适配器）。如果未指定，则仅允许使用使  用基础模型   scaling   factor   训练的   adapters （适配器）。  --max-cpu-loras   存储在   CPU   内存中的   LoRA   的最大数量。必须   >=   max_loras 。  --fully-sharded-loras   默认情况下，只有一半的   LoRA   计算通过   tensor   parallelism （张  量并行）进行分片。启用此选项将使用   fully   sharded   layers （完全分片层）。在高序  列长度、最大   rank （秩）或   tensor   parallel   size （张量并行大小）下，这可能更快。  默认值： False  --enable-prompt-adapter   如果为   True ，启用   PromptAdapters （ Prompt   适配器）的处  理。

## 第25页

默认值： False  --max-prompt-adapters   一个   batch （批次）中   PromptAdapters （ Prompt   适配器）的  最大数量。  默认值： 1  --max-prompt-adapter-tokenPromptAdapters   tokens （ Prompt   适配器令牌）的最大数  量  默认值： 0  --device   可选选项： auto,   cuda,   neuron,   cpu,   tpu,   xpu,   hpu  vLLM   执行的   device   type （设备类型）。  默认值： “ auto ”  --num-scheduler-steps   每个   scheduler   call （调度器调用）的最大   forward   steps （前  向步骤）数。  默认值： 1  --use-tqdm-on-load,   --no-use-tqdm-on-load   加载模型权重时是否启用 / 禁用进度条。  默认值： True  --multi-step-stream-outputs   如果为   False ，则   multi-step （多步）将在所有步骤结束时  stream   outputs （流式输出）  默认值： True

## 第26页

--scheduler-delay-factor   在调度下一个   prompt （提示）之前，应用延迟（延迟因子乘  以先前的   prompt   latency （提示延迟））。  默认值： 0.0  --enable-chunked-prefill   如果设置， prefill   requests （预填充请求）可以基于  max_num_batched_tokens   进行分块。  --speculative-configspeculative   decoding （推测解码）的配置。应为   JSON   字符串。  --model-loader-extra-configmodel   loader （模型加载器）的额外配置。这将传递给与  所选   load_format （加载格式）对应的   model   loader （模型加载器）。这应该是一个  JSON   字符串，将被解析为一个字典。  --ignore-patterns   加载模型时要忽略的   pattern （模式）。默认值为   original/**/* ，以避  免重复加载   llama   的   checkpoints （检查点）。  默认值： []  --preemption-mode   如果为   ‘ recompute ’ ，引擎通过重新计算执行   preemption （抢  占）；如果为   ‘ swap ’ ，引擎通过   block   swapping （块交换）执行   preemption （抢  占）。  --served-model-nameAPI   中使用的   model   name(s) （模型名称）。如果提供了多个名  称，服务器将响应任何提供的名称。响应的   model   字段中的模型名称将是列表中的第  一个名称。如果未指定，模型名称将与   <span   class="pre">--model</span>   参数  相同。请注意，如果提供多个名称，此名称也将用于   prometheus   metrics （普罗米修  斯指标）的   model_name   tag   content （标签内容）中， metrics   tag （指标标签）将采  用第一个名称。  --qlora-adapter-name-or-pathQLoRA   adapter （ QLoRA   适配器）的名称或路径。

## 第27页

--show-hidden-metrics-for-version   启用自指定版本以来已隐藏的   deprecated （已弃  用）   Prometheus   metrics （普罗米修斯指标）。例如，如果先前已弃用的   metric （指  标）自   v0.7.0   版本以来已被隐藏，您可以使用   – show-hidden-metrics-for-version=0.7  作为临时应急方案，同时迁移到新   metrics （指标）。该   metric （指标）很可能在即将  发布的版本中被完全删除。  --otlp-traces-endpointOpenTelemetry   traces （ OpenTelemetry   追踪）将被发送到的目  标   URL 。  --collect-detailed-traces   有效选项为   model,   worker,   all 。仅当设置了   <span  class="pre">--otlp-traces-endpoint</span>   时，设置此项才有意义。如果设  置，它将为指定的模块收集   detailed   traces （详细追踪）。这涉及使用可能代价高昂  和 / 或阻塞的操作，因此可能会对性能产生影响。  --disable-async-output-proc   禁用   async   output   processing （异步输出处理）。这可能  会导致性能降低。  默认值： False  --scheduling-policy   可选选项： fcfs,   priority  要使用的   scheduling   policy （调度策略）。 “ fcfs ” （先到先服务，即按照到达顺序处理  请求；默认）或   “ priority ” （基于给定的   priority （优先级）处理请求（值越低表示越早  处理），并以到达时间决定任何并列情况）。  默认值： “ fcfs ”  --scheduler-cls   要使用的   scheduler   class （调度器类）。  “ vllm.core.scheduler.Scheduler ”   是默认的   scheduler （调度器）。可以是直接的类，  也可以是   “ mod.custom_class ”   形式的类路径。  默认值： “ vllm.core.scheduler.Scheduler ”

## 第28页

--override-neuron-config   覆盖或设置   neuron   device   configuration （ neuron   设备配  置）。例如： <span  class="pre">{"cast_logits_dtype":</span><span>   </span><span  class="pre">"bloat16"}</span> 。  --override-pooler-config   覆盖或设置   pooling   models （池化模型）的   pooling   method  （池化方法）。例如： <span  class="pre">{"pooling_type":</span><span>   </span><span  class="pre">"mean",</span><span>   </span><span  class="pre">"normalize":</span><span>   </span><span  class="pre">false}</span> 。  --compilation-config,   -O   模型的   torch.compile   配置。当它是一个数字（ 0,   1,   2,   3 ）  时，它将被解释为   optimization   level （优化级别）。注意：级别   0   是默认级别，没有  任何优化。级别   1   和   2   仅用于内部测试。级别   3   是推荐用于生产的级别。要指定完整  的   compilation   config （编译配置），请使用   JSON   字符串。按照传统编译器的惯例，  也支持不带空格地使用   -O 。 -O3   等同于   -O   3 。  --kv-transfer-configdistributed   KV   cache   transfer （分布式   KV   缓存传输）的配置。应  为   JSON   字符串。  --worker-cls   用于   distributed   execution （分布式执行）的   worker   class （工作进程  类）。  默认值： “ auto ”  --worker-extension-clsworker   cls （工作进程类）之上的   worker   extension   class （工作  进程扩展类），如果您只想向   worker   class （工作进程类）添加新功能而不更改现有  功能，这将非常有用。  默认值： “”  --generation-configgeneration   config （生成配置）的文件夹路径。默认为   ‘ auto ’ ，  generation   config （生成配置）将从模型路径加载。如果设置为   ‘ vllm ’ ，则不加载  generation   config （生成配置），将使用   vLLM   默认值。如果设置为文件夹路径，

## 第29页

generation   config （生成配置）将从指定的文件夹路径加载。如果在   generation   config  （生成配置）中指定了   max_new_tokens ，则它将为所有请求设置服务器范围内的输  出   tokens （令牌）数量限制。  默认值： auto  --override-generation-config   以   JSON   格式覆盖或设置   generation   config （生成配  置）。例如： <span  class="pre">{"temperature":</span><span>   </span><span  class="pre">0.5}</span> 。如果与   – generation-config=auto   一起使用， override  parameters （覆盖参数）将与模型的默认配置合并。如果   generation-config   为  None ，则仅使用   override   parameters （覆盖参数）。  --enable-sleep-mode   为引擎启用   sleep   mode （睡眠模式）。（仅支持   cuda   平台）  默认值： False  --calculate-kv-scales   当   kv-cache-dtype   为   fp8   时，启用   k_scale   和   v_scale   的动态计  算。如果   calculate-kv-scales   为   false ，则   scales （缩放）将从模型   checkpoint （检查  点）加载（如果可用）。否则， scales （缩放）将默认为   1.0 。  默认值： False  --additional-configJSON   格式的指定平台的   additional   config （附加配置）。不同的平  台可能支持不同的配置。确保配置对于您正在使用的平台有效。输入格式类似于  ‘ { “ config_key ” : ” config_value ” } ’  --enable-reasoning   是否为模型启用   reasoning_content （推理内容）。如果启用，模  型将能够生成   reasoning   content （推理内容）。  默认值： False  --reasoning-parser   可选选项： deepseek_r1,   granite

## 第30页

根据您正在使用的模型选择   reasoning   parser （推理解析器）。这用于将   reasoning  content （推理内容）解析为   OpenAI   API   格式。   <span   class="pre">--enable-  reasoning</span>   需要此项。  --disable-cascade-attn   为   V1   禁用   cascade   attention （级联注意力）。虽然   cascade  attention （级联注意力）不会改变数学上的正确性，但禁用它可以用于防止潜在的数  值问题。请注意，即使将其设置为   False ， cascade   attention （级联注意力）也仅在  heuristic （启发式）表明它有利时才使用。  默认值： False  --disable-chunked-mm-input   为   V1   禁用   multimodal   input   chunking   attention （多模态  输入分块注意力）。如果设置为   true   并且启用了   chunked   prefill （分块预填充），我  们不希望部分调度   multimodal   item （多模态项目）。这确保了如果一个请求具有混合  prompt （提示）（例如文本   tokens   TTTT   后跟图像   tokens   IIIIIIIIII ），其中只能调度一  些图像   tokens （例如   TTTTIIIII ，留下   IIIII ），它将分步调度为   TTTT   和   IIIIIIIIII 。  默认值： False  --disable-log-requests   禁用   logging   requests （请求日志记录）。  默认值： False  --max-log-len   日志中打印的最大   prompt   characters （提示字符）或   prompt   ID  numbers （提示   ID   号）数量。默认值   None   表示无限制。  --disable-fastapi-docs   禁用   FastAPI   的   OpenAPI   schema （ OpenAPI   模式）、  Swagger   UI   和   ReDoc   endpoint （ ReDoc   端点）。  默认值： False  --enable-prompt-tokens-details   如果设置为   True ，则在   usage （用量）中启用

## 第31页

prompt_tokens_details 。  默认值： False  --enable-server-load-tracking   如果设置为   True ，则在   app   state （应用状态）中启用  tracking   server_load_metrics （跟踪服务器负载指标）。  默认值： False  Qwen3   的部署命令和   API   调用  Plain   Text  python   -m   vllm.entrypoints.openai.api_server   \  --model   /root/autodl-tmp/models/Qwen/Qwen3-8B   \  --served-model-name   qwen3-8b   \  --max-model-len   8k   \  --host   0.0.0.0   \  --port   6006   \  --dtype   bfloat16   \  --gpu-memory-utilization   0.8   \  --enable-auto-tool-choice   \  --tool-call-parser   hermes   \  --enable-reasoning   \  --reasoning-parser   deepseek_r1   \  python   -m   vllm.entrypoints.openai.api_server   \  --model   /root/autodl-tmp/models/Qwen/Qwen2___5-Omni-3B   \  --served-model-name   qwen-omni-3b   \  --max-model-len   16k   \  --host   0.0.0.0   \  --port   6006   \  --dtype   float16   \  --gpu-memory-utilization   0.8  --   deepseek-r1-0528-qwen3-8B  python   -m   vllm.entrypoints.openai.api_server   \

## 第32页

--model   /root/autodl-tmp/models/deepseek-ai/DeepSeek-R1-0528-  Qwen3-8B   \  --served-model-name   ds-qwen3-8b   \  --max-model-len   8k   \  --host   0.0.0.0   \  --port   6006   \  --dtype   bfloat16   \  --gpu-memory-utilization   0.8   \  --enable-auto-tool-choice   \  --tool-call-parser   hermes  第二章、新版   LangChain   的应用开发  开发环境：   Pycharm-2025   版 +   Python-3.11   +   JDK-17   +   SpringAI(1.0.0-M7)-   Spring-  boot(3.44)   langchain

## 第33页

架构  LangChain   作为一个框架由多个包组成。  •   langchain-core  该包包含不同组件的基本抽象以及将它们组合在一起的方法。   核心组件的接口，如大  型语言模型、向量存储、检索器等在此定义。   此处未定义任何第三方集成。   依赖项故  意保持非常轻量级。  •   langchain  主要的   langchain   包含链、代理和检索策略，这些构成了应用程序的认知架构。   这  些不是第三方集成。   这里的所有链、代理和检索策略并不特定于任何一个集成，而是  适用于所有集成的通用策略。  •   langchain-community  此包包含由   LangChain   社区维护的第三方集成。   关键的合作伙伴包被单独列出（见下  文）。   这包含了各种组件（大型语言模型、向量存储、检索器）的所有集成。   此包中  的所有依赖项都是可选的，以保持包尽可能轻量。  1 、连接   AI   大模型   和   提示词模板  小爱   AI   的注册地址： https://xiaoai.plus/register?aff=3TIp  一、连接   AI   大模型  LangChain   不托管任何聊天模型，而是依赖于第三方集成。官网如下：  https://www.langchain.com.cn/docs/integrations/chat/  在构建   ChatModels   时，我们有一些标准化参数：

## 第34页

•   model :   模型名称  •   temperature :   采样温度  •   timeout :   请求超时  •   max_tokens :   生成的最大令牌数  •   stop :   默认停止序列  •   max_retries :   请求重试的最大次数  •   api_key :   大模型供应商的   API   密钥  •   base_url :   发送请求的端点  一些重要事项需要注意：  •   标准参数仅适用于公开具有预期功能的参数的大模型供应商。例如，一些大模型  供应商不公开最大输出令牌的配置，因此在这些大模型供应商上无法支 持  max_tokens 。  •   标准参数目前仅在具有自己集成包的集成上强制执行（例如   langchain-  openai 、 langchain-anthropic   等），在   langchain-community   中的模型上不强  制执行。  二、提示词模板  提示词模板有助于将用户输入和参数转换为语言模型的指令。   这可以用于指导模型的  响应，帮助其理解上下文并生成相关且连贯的基于语言的输出。  提示词模板的输入是一个字典，其中每个键表示要填充的提示词模板中的变量。  有两种类型的提示词模板：  字符串提示词模板  这些提示词模板用于格式化单个字符串，通常用于更简单的输入。   例如，构造和使用  PromptTemplate   的一种常见方式如下：  Python  prompt_template   =   PromptTemplate.from_template(" 帮我生成一个简短的，  关于 {topic} 的报幕词。 ")

## 第35页

prompt_template.invoke({"topic":   " 相声 "})  In-context   Learning （ ICL ）作为一种新的自然语言处理范式逐渐崭露头角。 ICL   的核  心思想是：通过提供少量示例作为上下文，让大模型直接从中学习并做出预测。这一  方法不仅省去了传统监督学习中繁琐的训练过程，还为大模型的应用开辟了新的可能  性。  聊天提示词模板  这些提示词模板用于格式化消息列表。这些 “ 模板 ” 本身由一系列模板组成。   例如，构  建和使用   ChatPromptTemplate   的一种常见方式如下：  Python  from   langchain_core.prompts   import   ChatPromptTemplate  prompt_template   =   ChatPromptTemplate.from_messages([  ("system",   " 你是一个幽默的电视台主持人！ "),  ("user",   " 帮我生成一个简短的，关于 {topic} 的报幕词。 ")  ])  prompt_template.invoke({"topic":   " 相声 "})  在上述示例中，当调用此   ChatPromptTemplate   时，将构造两个消息。   第一个是系统  消息，没有变量需要格式化。   第二个是   HumanMessage ，将由用户传入的   topic   变  量进行格式化。  消息占位符  此提示词模板负责在特定位置添加消息列表。   在上面的   ChatPromptTemplate   中，我  们看到如何格式化两个消息，每个消息都是一个字符串。   但是如果我们希望用户传入  一个消息列表（历史消息），并将其插入到特定位置呢？   这就是需要使用  MessagesPlaceholder 。  Python  from   langchain_core.prompts   import   ChatPromptTemplate,  MessagesPlaceholder  from   langchain_core.messages   import   HumanMessage  prompt_template   =   ChatPromptTemplate.from_messages([  ("system",   " 你是一个电视台，高端访谈节目的主持人！ "),  MessagesPlaceholder("msgs")  ])

## 第36页

prompt_template.invoke({"msgs":   [HumanMessage(content=" 你好，主持  人 !")]})  这将生成一个包含两个消息的列表，第一个是系统消息，第二个是我们传入的  HumanMessage 。后面的消息就是我   和   AI   大模型对话过程中的历史消息。   这对于将  消息列表插入到特定位置非常有用。  SQL  prompt   =   ChatPromptTemplate.from_messages([  ('system',   ' 你是一个智能助手，尽可能的调用工具回答用户的问题 '),  MessagesPlaceholder(variable_name='chat_history',  optional=True),  ('human',   '{input}'),  MessagesPlaceholder(variable_name='agent_scratchpad',  optional=True),  ])  2 、输出解析器和结构化输出  输出解析器   ：负责获取模型的输出并将其转换为更适合下游任务的格式。   在使用大型  语言模型生成结构化数据或规范化聊天模型和大型语言模型的输出时非常有用。  大型语言模型能够生成任意文本。这使得模型能够适当地响应广泛的   输入范围，但对  于某些用例，限制大型语言模型的输出   为特定格式或结构是有用的。这被称为 结构化  输出 。  例如，如果输出要存储在关系数据库中，   如果模型生成遵循定义的模式或格式的输  出，将会容易得多。   最常见的输出格式将是   JSON ，   尽管其他格式如   YAML   也可能  很有用。  .with_structured_output()  为了方便，一些   LangChain   聊天模型支持 .with_structured_output() 方法。   该方  法只需要一个模式作为输入，并返回一个字典或   Pydantic   对象。   通常，这个方法仅在  支持下面描述的更高级方法的模型上存在，   并将在内部使用其中一种。它负责导入合  适的输出解析器并   将模式格式化为模型所需的正确格式。  Python  import   json

## 第37页

from   typing   import   Optional  from   langchain_core.messages   import   HumanMessage  from   langchain_core.output_parsers   import   StrOutputParser  from   langchain_core.prompts   import   MessagesPlaceholder,   \  FewShotChatMessagePromptTemplate,   PromptTemplate  from   pydantic   import   BaseModel,   Field  from   langchain_demo.my_llm   import   llm  from   langchain_core.prompts   import   ChatPromptTemplate  #  生成一个笑话的段子：   三个属性，  #  使用   pydantic  定义一个类  class   Joke(BaseModel):  """  笑话（搞笑段子）的结构类 (  数据模型类   POVO)"""  setup:   str   =   Field(description=" 笑话的开头部分 ")   #  笑话的铺垫部  分  punchline:   str   =   Field(description=" 笑话的包袱 / 笑点 ")   #  笑话的  爆笑部分  rating:   Optional[int]   =   Field(description=" 笑话的有趣程度评分，  范围   1   到   10")   #  可选的笑话评分字段  prompt_template   =   PromptTemplate.from_template(" 帮我生成一个关于  {topic} 的笑话。 ")  runnable   =   llm.with_structured_output(Joke)  chain   =   prompt_template   |   runnable  resp   =   chain.invoke({"topic":   " 猫 "})  print(resp)  print(resp.__dict__)  json_str   =   json.dumps(resp.__dict__)  print(json_str)  SimpleJsonOutputParser  一些模型，例如   Mistral 、 OpenAI ，   Together   AI   和   Ollama ，   支持一种称为   JSON   模

## 第38页

式   的功能，通常通过配置启用。启用时， JSON   模式将限制模型的输出始终为某种有  效的   JSON 。  Python  #  创建聊天提示模板，要求模型以特定格式回答问题  prompt   =   ChatPromptTemplate.from_template(  " 尽你所能回答用户的问题。 "   #  基本指令  ' 你必须始终输出一个包含 "answer" 和 "followup_question" 键的   JSON   对  象。其中 "answer" 代表：对用户问题的回答； "followup_question" 代表：用户  可能提出的后续问题 '  "{question}"   #  用户问题占位符  )  chain   =   prompt   |   llm   |   SimpleJsonOutputParser()  resp   =   chain.invoke({"question":   " 细胞的动力源是什么？ "})  print(resp)  工具调用  对于支持此功能的模型，工具调用   可以非常方便地生成结构化输出。它消除了   关于如  何最好地提示模式的猜测，而是采用内置模型功能。  它的工作原理是首先将所需的模式直接或通过   LangChain   工具   绑定到   聊天模型，使  用   .bind_tools()   方法。然后模型将生成一个包含   与所需形状匹配的   args   的   tool_calls  字段的   AIMessage 。工具调用是一种通常一致的方法，可以让模型生成结构化输出，  并且是默认技术   用于   .with_structured_output()   方法，当模型支持时。  Python  class   ResponseFormatter(BaseModel):  """ 始终使用此工具来结构化你的用户响应 """   #  文档字符串说明这个类用

## 第39页

于格式化响应  answer:   str   =   Field(description=" 对用户问题的回答 ")   #  回答内容  字段  followup_question:   str   =   Field(description=" 用户可能提出的后续问  题 ")   #  后续问题字段  runnable   =   llm.bind_tools([ResponseFormatter])  resp   =   runnable.invoke(" 细胞的动力源是什么？ ")  print(resp.tool_calls[-1]['args'])  resp.pretty_print()  3 、大模型应用开发案例  一、多模态的聊天机器人  1.   多模型调用和多模态模型的调用  2.   保存历史聊天记录  3.   修剪聊天上下文  4.   形成摘要记忆  5.   拥有   web   界面，方便用户使用  6.   可以在线录制语音  7.   可以处理语音、图片和视频  注意：   目前所有的多模态大模型，如果需要传入多媒体内容。只有两种方式：  1 、传入多媒体文件的网络访问路径，比如 :   http://www..baidu.com/log.png  2 、把多媒体文件转换为   base64   格式的字符串，再传入大模型。

## 第40页

4 、 RAG   和   Embeddings   模型  一、什么是   Embedding   模型  Embedding   模型是指将高维度的数据（例如文字、图片、视频）映射到低维度空间的  过程。简单来说， embedding   向量就是一个   N   维的实值向量，它将输入的数据表示成  一个连续的数值空间中的点。  Embeddings   的学习通常基于无监督或弱监督的方法。对于自然语言处理任务，常用  的   Embeddings   方法包括   Word2Vec 、 GloVe   和   FastText 。这些方法可以从大规模的  文本语料库中学习单词的分布式表示。对于计算机视觉任务，常用的   Embeddings   方  法包括卷积神经网络（ CNN ）和循环神经网络（ RNN ）等。  通俗易懂的描述： 嵌入就相当于给文本穿上了 “ 数字化 ” 的外衣 ，目的是让机器更好的  理解和处理。  发展： 由静态的   Word   Embedding （如   Word2Vec 、 GloVe   和   FastText ）   ->   动态预训  练模型（如   ELMo 、 BERT 、 GPT 、 GPT-2 、 GPT-3 、 ALBERT 、 XLNet   等）。大型语  言模型可以生成上下文相关的   embedding   表示，可以更好地捕捉单词的语义和上下文

## 第41页

信息。  向量空间（ Vector   Space ）  所有的数据都变成向量，这些向量组成一个庞大的矩阵。在这个世界里，每个词、句  子、图片、用户 ... 都被表示成一个 “ 点 ” （即向量），大家都有自己的 “ 坐标 ” 。  我们可以通过 “ 距离 ” 和 “ 方向 ” 来理解它们的关系。  Embedding   向量放在向量空间里，有啥用？  距离表示相似度  向量之间越近：意义越相似  向量之间越远：意义越不同  比如：  “ 苹果   ”   和   “ 香蕉   ”   的向量夹角小（近）   →   都是水果  “ 苹果   ”   和   “ MacBook   ”   的向量略远   →   一个是水果，一个是电子产品  使用场景

## 第42页

1.   Embeddings   可以在各种机器学习任务中使用，包括分类、聚类、检索和推荐  等。  2.   在自然语言处理任务中，可以使用静态预训练的   Embeddings   模型， 如  Word2Vec 、 GloVe   和   FastText ，来生成单词的向量表示。这些预训练的   Embedding s  模型通常在大规模的文本数据上进行训练，可以用于处理不同的自然语言处理任务，  如情感分析、命名实体识别和机器翻译等。  3.   在计算机视觉任务中，可以使用卷积神经网络（ CNN ）提取图像的特征向量，然  后使用这些特征向量进行分类、检索和生成等任务。另外，通过将图像与文本进行联  合训练，可以学习到图像和文本之间的语义关系，从而实现图像与文本的检索和生成  等任务。  4.   我们在做   RGA   开发时又会涉及到向量数据库，在创建向量数据库时又需要使 用  Embedding   模型对文本进行向量化处理。在检索的时候，需要对用户输入进行向量化  处理也需要用到。  解决问题  •   降维：在高维度空间中，数据点之间可能存在很大的距离，使得样本稀疏，嵌入  模型可以减少数据稀疏性。  •   捕捉语义信息： Embedding   不仅仅是降维，更重要的是，它能够捕捉到数据的语  义信息。语义相近的词在向量上也是相近的  •   特征表示：原始数据的特征往往难以直接使用，通过嵌入模型可以将特征转换成  更有意义的表示。  •   计算效率：在低维度空间中对数据进行处理和分析往往更加高效。  独热编码（ One-Hot   Encoding ）  是一种将数据转换为二进制向量的技术。它的主要目的是将分类变量转换为机器学习  算法能够处理的格式，从而避免数值关系的误判。  举例：词表中有   10,000   个词，每个词都用一个只有一个   1 ，其它全是   0   的向量来表  示。

## 第43页

这样的向量是：  高维（非常长，比如   10k 、 100k ... ）  ⚪   稀疏（只有一个   1 ，其他都是   0 ）  没有语义信息（ “ 猫 ” 和 “ 狗 ” 之间毫无关系）  二、 langchain   的文本嵌入模型 (Embeddings)  嵌入模型创建文本片段的向量表示。您可以将向量视为一个数字数组，它捕捉了文本  的语义含义。   通过这种方式表示文本，您可以执行数学运算，从而进行诸如搜索其他  在意义上最相似的文本等操作。  Embeddings   类是一个用于与文本嵌入模型接口的类。有很多嵌入大模型供应商  （ OpenAI 、 Hugging   Face ， BGE   等）   -   这个类旨在为它们提供一个标准接口。  LangChain   中的基础   Embeddings   类提供了两个方法：一个用于嵌入文档，一个用于  嵌入查询。前者， .embed_documents ，接受多个文本作为输入，而后  者， .embed_query ，接受单个文本。将这两个方法分开是因为某些嵌入大模型供应商

## 第44页

对文档（待搜索的内容）和查询（搜索查询本身）有不同的嵌入方  法。   .embed_query   将返回一个浮点数列表，而   .embed_documents   返回一个浮点数  列表的列表。  三、私有化部署   Qwen3-Embedding  生产环境中的   Embeddings   模型对比  点击图片可查看完整电子表格  为了部署   Embedding   模型，我们需要引入对应的工具库，目前主要有几类：  1.   Sentence-Transformers :   Sentence-Transformers   库是基于   HuggingFace   的  Transformers   库构建的，它专门设计用于生成句子级别的嵌入。它引入了一些特定的  模型和池化技术，使得生成的嵌入能够更好地捕捉句子的语义信息。 Sentence-  Transformers   库特别适合于需要计算句子相似度、进行语义搜索和挖掘同义词等任

## 第45页

务。  2.   HuggingFace   Transformers :   HuggingFace   的   Transformers   库是一个广泛使用  的   NLP   库，它提供了多种预训练模型，如   BERT 、 GPT-2 、 RoBERTa   等。这些模型  可以应用于各种   NLP   任务，如文本分类、命名实体识别、问答系统等。 Transformer s  库支持多种编程语言，并且支持模型的微调和自定义模型的创建。虽然   Transformer s  库的功能强大，但它主要关注于模型的使用，而不是直接提供句子级别的嵌入。  3.   Langchain   集成 的   HuggingFaceBgeEmbeddings 。与   3   一样。  4.   FlagEmbedding:   这是一个相对较新的库，其核心在于能够将任意文本映射到低  维稠密向量空间，以便于后续的检索、分类、聚类或语义匹配等任务。  FlagEmbedding   的一大特色是它可以支持为大模型调用外部知识，这意味着它不仅可  以处理纯文本数据，还能整合其他类型的信息源，如知识图谱等，以提供更丰富的语  义表示。  总的来说， FlagEmbedding   强调的是稠密向量的生成和外部知识的融合；  HuggingFace   Transformers   提供了一个广泛的预训练模型集合，适用于多种   NLP   任  务；而   Sentence-Transformers   则专注于生成高质量的句子嵌入，适合那些需要深入  理解句子语义的应用场景。  四、 BGE-Large   的   Embadding+Huggingface   私有化  HuggingFace   上的   BGE   模型是最好的开源嵌入模型之一。   BGE   模型由北京人工智能  研究院   （ BAAI ）   创建。   是一家从事   AI   研发的私营非营利组织。  BGE-Large （智源研究院）和   GTE-Large （阿里巴巴）（ 6   月之前 ）是当前中文   RA G  领域主流的开源   Embedding   模型，两者的核心区别与优势如下：  配置   HuggingFace   镜像站： https://hf-mirror.com/

## 第46页

Plain   Text  pip   install   --upgrade   --quiet   sentence_transformers  Plain   Text  from   langchain.embeddings   import   HuggingFaceBgeEmbeddings  model_name   =   "BAAI/bge-large-zh-v1.5"  model_kwargs   =   {'device':   'cuda'}  encode_kwargs   =   {'normalize_embeddings':   True}   #   set   True   to  compute   cosine   similarity  model   =   HuggingFaceBgeEmbeddings(  model_name=model_name,  model_kwargs=model_kwargs,  encode_kwargs=encode_kwargs,  query_instruction=" 为这个句子生成表示以用于检索相关文章： "  )

## 第47页

model.query_instruction   =   " 为这个句子生成表示以用于检索相关文章： "  在   HuggingFaceBgeEmbeddings   中， normalize_embeddings   参数通常只接受布尔  值（ True   或   False ），用于决定是否对生成的嵌入向量进行归一化处理。具体来说：  •   True ：生成的嵌入向量会被归一化为单位向量。这意味着每个嵌入向量的   L2   范  数（欧几里得长度）将被缩放到   1 。  •   False ：生成的嵌入向量将保持原始的数值，不进行归一化处理。  •   优点   ：  •   提高相似度计算的稳定性   ：在许多应用场景中，如余弦相似度计算，归一化后的  向量可以避免因向量长度不同而导致的相似度偏差，使相似度计算更加专注于向量的  方向而非长度。  •   一致性   ：在某些情况下，归一化可以确保不同批次或不同模型生成的嵌入向量在  同一尺度上，便于比较和整合。  案例：根据语义搜索美食评论数据  余弦距离（ Cosine   Distance ） ​   的计算，用于衡量两个向量在方向上的相似性。代  表   文本语义的相似性  ||a||   ：   计算向量   a   的欧几里得范数（ L2   范数），即向量的长度。公式为   sqrt(a ₁²   +  a ₂²   +   ...   +   a ₙ   ² )

## 第48页

ab ：   计算向量   a   和   b   的点积（内积），即对应元素相乘后求和。  五、向量数据库  存储和搜索非结构化数据的最常见方法之一是将其嵌入并存储生成的嵌入向量，   然后  在查询时嵌入非结构化查询并检索与嵌入查询 “ 最相似 ” 的嵌入向量。   向量存储负责存  储嵌入数据并执行向量搜索，   为您处理这些。  Chroma  Chroma   是一个开源的向量数据库，专注于简化文本嵌入的存储和检索过程。 Chroma  采用   Apache   2.0   许可证。它的主要特点包括：  1.   支持多种存储后端 ： Chroma   支持多种底层存储选项，如   DuckDB （适用于独立  应用）和   ClickHouse （适用于大规模扩展）。  2.   多语言支持 ： Chroma   提供了   Python   和   JavaScript/ TypeScript   的   SDK ，方便开  发者快速集成。  3.   简单易用 ： Chroma   的设计理念是 “ 简单至上 ” ，旨在提升开发者的效率。  4.   高性能 ： Chroma   不仅支持快速的相似度搜索，还提供了对搜索结果的分析功  能。  FAISS  Faiss   是由   Facebook   AI   Research   团队开发的一个库，旨在高效地进行大规模向量相  似性搜索。它不仅支持   CPU ，还能利用   GPU   进行加速，非常适合处理大量高维数  据。 Faiss   提供了多种索引类型，以适应不同的需求，从简单的平面索引（ Flat  Index ）到更复杂的倒排文件索引（ IVF ）和乘积量化索引（ PQ ）。  Milvus  Milvus   基本介绍  •   Milvus   由   Zilliz   开发，并捐赠给了   Linux   基金会下的   LF   AI   &   Data   基金会，现已  成为世界领先的开源向量数据库项目之一  ￮   什么是向量数据库：传统的数据库主要处理结构化数据，而向量数据库则专  注于处理非结构化数据经过嵌入模型（ embedding   model ）转换而来的向量数  据。这些向量是高维空间中的点，它们捕获了原始数据的语义信息。向量数据库  的核心能力是进行 相似性搜索 ，即根据查询向量找到最相似的向量，从而实现语

## 第49页

义级别的搜索和匹配。  •   Milvus   采用   Apache   2.0   许可发布，大多数贡献者都是高性能计算（ HPC ）领域  的专家，擅长构建大规模系统和优化硬件感知代码  六、 RAG   案例  RAG ： Retrieval-Augmented   Generation   检索增强生成。 RAG   通过结合   LLMs   的内在  知识和外部数据库的非参数化数据，提高了模型在知识密集型任务中的准确性和可信  度。  上下文感知的检索器

## 第50页

第三章、基于   LangGraph   的   Agent  LangGraph   专为希望构建强大、适应性强的   AI   智能体的开发者而设计。开发者选择  LangGraph   的原因是：  •   可靠性和可控性。 通过审核检查和人工干预审批来指导智能体行为。 LangGraph  可为长时间运行的工作流持久化上下文，使您的智能体保持正常运行。  •   低层级和可扩展性。 使用完全描述性的低层级原语构建自定义智能体，不受限制  自定义的僵化抽象约束。设计可扩展的多智能体系统，其中每个智能体都为您的用例  量身定制特定角色。  •   一流的流式传输支持。 通过逐令牌流式传输和中间步骤流式传输， LangGraph   让  用户实时清晰地了解智能体的推理和行动过程。  LangGraph   支持两种对于构建对话代理至关重要的内存类型：  •   短期内存 ：通过在会话中维护消息历史来跟踪正在进行的对话。  •   长期内存 ：在不同会话之间存储用户特定或应用程序级别的数据。

## 第52页

什么是   Agent ？  人类在复杂的模式识别任务中表现卓越，但通常需要借助工具（如书籍、搜索引擎或  计算器）来补充先验知识以得出结论。同理，生成式   AI   模型可通过训练使用工具获取  实时信息或建议的实际动作。例如：  •   模型可利用数据库检索工具获取客户购买历史以生成个性化购物推荐  •   基于用户查询，模型可通过   API   调用发送邮件或完成金融交易  为实现此能力，模型需具备：  1.   外部工具集访问权限  2.   自主规划与执行任务的推理能力  这种结合推理逻辑与外部信息访问的系统，即构成智能体（ Agent ）。

## 第53页

智能体的认知架构中有三个基本组件：模型（ Model ）、工具（ Tools ）和以及一个提  供指令的 提示 。  LLM   在一个循环中运行。在每次迭代中，它会选择一个要调用的工具，提供输入，接  收结果（一个观察），并利用该观察来指导下一个动作。循环会一直持续， 直到满足  停止条件 —— 通常是   Agent   已经收集到足够的信息来响应用户时。  Agent   vs.   Workflow （图）  Anthropic   将   Agent   系统划分为两类：  1.   第一类是   workflow 。遵循预定义的工作流，编排   LLM   和工具，固定代码路径。  2.   Agent ：此类   Agent   被定义为完全自主的系统，这些系统在较长时间内独立运  行，可以动态地指导自身流程和工具使用的系统。通过自身的推理、规划能力，自主  控制，完成任务。  注意：在   LangGraph   中，一切都是图， Agent   是图中的一个节点。使用  create_react_agent   创建一个   Agent ，并且也得到了一个图。

## 第54页

以下代码片段展示了如何使用   create_react_agent   创建上述   Agent  Python  from   langgraph.prebuilt   import   create_react_agent  from   langchain_openai   import   ChatOpenAI  model   =   ChatOpenAI("xxx")  def   tool()   ->   None:  """Testing   tool."""  ...  agent   =   create_react_agent(  model,  tools=[tool],  )  agent.get_graph().draw_mermaid_png()  1 、 LangGraph   本地服务

## 第55页

LangGraph   CLI   是一个多平台命令行工具，用于在本地构建和运行   LangGraph   API  服务器。生成的服务器包含您的图的所有运行、线程、助手等的   API   端点，以及运行  您的代理所需的其他服务，包括用于检查点和存储的托管数据库。  安装和使用步骤  一、创建   Python   虚拟环境  虚拟环境的安装步骤  1.   安装好   python   解释器：   Python   >=   3.11   is   required.  2.   安装虚拟环境库，在   cmd   中输入：  Plain   Text  pip   install   virtualenv  3.   创建虚拟环境，在   cmd   中切换到需要创建虚拟环境的目录下，执行：

## 第56页

Plain   Text  virtualenv   env_name  4.   激活虚拟环境，在   cmd   中进入到   第三步创建的   env_name/Scripts   目录下，执  行：  Plain   Text  activate  执行成功后，在   cmd   中，当前输入行前面会有   (env_name)   的前缀  在当前状态下，使用   pip   就是在虚拟环境中安装第三方库了  5.   退出虚拟环境， cmd   中输入：  Plain   Text  deactivate  二、安装   LangGraph   CLI  Python  #   Python   >=   3.11   is   required.  pip   install   --upgrade   "langgraph-cli[inmem]"  三、创建   LangGraph   应用  从   new-langgraph-project-python   模板 或   new-langgraph-project-js   模板 创建  一个新应用。此模板演示了一个单节点应用，您可以根据自己的逻辑进行扩展。  注意 : 如果您使用   langgraph   new   命令时未指定模板，将显示一个交互式菜单，允许  您从可用模板列表中进行选择。  Python  langgraph   new   path/to/your/app   --template   new-langgraph-project-  python  四、安装项目依赖  在您的新   LangGraph   应用的根目录下，以编辑模式安装依赖项，以便服务器使用您的  本地更改。  在   LangGraph   中， pyproject.toml   代传统的   setup.py   和   requirements.txt . 可

## 第57页

能包含以下扩展配置：  •   依赖分组 ​   ：如   [project.optional-dependencies]   定义   dev （开发工具）  和   test （测试框架）依赖。  •   动态版本控制 ​   ：通过   requires-python   =   ">=3.9"   指定   Python   版本兼容  性。  •   CI/CD   集成 ​   ：通过   [tool.*]   配置与   GitHub   Actions   或   GitLab   CI   的交互  Python  cd   path/to/your/app  pip   install   -e   .  五、修改   graph.py   的代码  Python  #  本地私有化部署的大模型  llm   =   ChatOpenAI(  model='qwen3-8b',  temperature=0.8,  api_key='xx',  base_url="http://localhost:6006/v1",  extra_body={'chat_template_kwargs':   {'enable_thinking':  False}},  )  def   get_weather(city:   str)   ->   str:  """Get   weather   for   a   given   city."""

## 第58页

return   f"It's   always   sunny   in   {city}!"  graph   =   create_react_agent(  llm,  tools=[get_weather],  prompt="You   are   a   helpful   assistant"  )  六、启动   LangGraph   服务器  langgraph   dev   命令以内存模式启动   LangGraph   服务器。此模式适用于开发和测试  目的。对于生产用途，请部署   LangGraph   服务器并使其能够访问持久存储后端。  Python  命令：   langgraph   dev  选项  点击图片可查看完整电子表格  七、测试和访问   agent   的   API  1.   LangGraph   Studio   是一个专用   UI ，您可以将其连接到   LangGraph   API   服务器，

## 第59页

以在本地可视化、交互和调试您的应用。通过访问   langgraph   dev   命令输出中提供的  URL ，在   LangGraph   Studio   中测试您的   Agent   和图。  2.   PythonSDK   测试  Shell  pip   install   langgraph-sdk  异步测试：  Python  from   langgraph_sdk   import   get_client  import   asyncio  client   =   get_client(url="http://localhost:2024")  async   def   main():  async   for   chunk   in   client.runs.stream(  None,   #   Threadless   run  "agent",   #   Name   of   assistant.   Defined   in   langgraph.json.  input={  "messages":   [{  "role":   "human",  "content":   "What   is   LangGraph?",  }],  },  ):  print(f"Receiving   new   event   of   type:   {chunk.event}...")  print(chunk.data)  print("\n\n")  asyncio.run(main())  同步测试：  Python  from   langgraph_sdk   import   get_sync_client  client   =   get_sync_client(url="http://localhost:2024")  for   chunk   in   client.runs.stream(  None,   #   Threadless   run  "agent",   #   Name   of   assistant.   Defined   in   langgraph.json.  input={

## 第60页

"messages":   [{  "role":   "human",  "content":   "What   is   LangGraph?",  }],  },  stream_mode="messages-tuple",  ):  print(f"Receiving   new   event   of   type:   {chunk.event}...")  print(chunk.data)  print("\n\n")  3.   JavaScript   SDK   测试  安装   LangGraph   JS   SDK  Shell  npm   install   @langchain/langgraph-sdk  向   LangGraph   服务区发送消息：  JavaScript  const   {   Client   }   =   await   import("@langchain/langgraph-sdk");  //   only   set   the   apiUrl   if   you   changed   the   default   port   when  calling   langgraph   dev  const   client   =   new   Client({   apiUrl:   "http://localhost:2024"});  const   streamResponse   =   client.runs.stream(  null,   //   Threadless   run  "agent",   //   Assistant   ID  {  input:   {  "messages":   [  {   "role":   "user",   "content":   "What   is   LangGraph?"}  ]  },  streamMode:   "messages-tuple",  }  );  for   await   (const   chunk   of   streamResponse)   {  console.log(`Receiving   new   event   of   type:   ${chunk.event}...`);  console.log(JSON.stringify(chunk.data));  console.log("\n\n");

## 第61页

}  4.   REST   API   测试：  Shell  curl   -s   --request   POST   \  --url   "http://localhost:2024/runs/stream"   \  --header   'Content-Type:   application/json'   \  --data   "{  \"assistant_id\":   \"agent\",  \"input\":   {  \"messages\":   [  {  \"role\":   \"human\",  \"content\":   \"What   is   LangGraph?\"  }  ]  },  \"stream_mode\":   \"messages-tuple\"  }"  2 、 Tool   工具的定义  在构建   Agent   时，您需要为其提供一个它可以使用的   工具   列表。除了实际调用的函数  之外，工具还包括几个组件：

## 第62页

注意：   如果工具具有精心选择的名称、描述和   args_schema ，模型将表现得更好。  LangChain   支持从以下对象创建工具  1.   函数；  2.   LangChain   Runnables ；  3.   通过从   BaseTool   子类化   --   这是最灵活的方法，它提供了最大的控制程度，但代  价是需要付出更多的努力和编写更多的代码。  一、从函数创建工具  这个   @tool   装饰器是定义自定义工具的最简单方法。默认情况下，装饰器使用函数名  称作为工具名称，但可以通过将字符串作为第一个参数传递来覆盖。此外，装饰器将  使用函数的文档字符串作为工具的描述   -   因此必须提供文档字符串。请注意， @tool  支持解析注释、嵌套模式和其他特性：  sglang   部署   Qwen-3-8B   模型  SQL  #   安装   sglang  pip   install   "sglang[all]>=0.4.6.post1"  #   启动大模型服务  python   -m   sglang.launch_server   \  --model-path   /hy-tmp/models/Qwen/Qwen3-8B   \  --served-model-name   qwen3-8b   \  --context-length   8192   \  --trust-remote-code   \  --host   0.0.0.0   \  --port   8080   \  --reasoning-parser   qwen3   \

## 第63页

--tool-call-parser   qwen25  二、从可运行对象（ Runnable ）创建工具  接受字符串或   dict   输入的   LangChain   Runnables   可以使用   as_tool   方法转换为工  具，该方法允许为参数指定名称、描述和其他模式信息。  三、子类化   BaseTool  可以通过从   BaseTool   子类化来定义自定义工具。这提供了对工具定义的最大控制，  但需要编写更多代码。  Python  class   SearchArgs(BaseModel):  query:   str   =   Field(description=" 需要进行网络搜索的信息。 ")  #  网络搜索的工具  class   MySearchTool(BaseTool):  #  工具名字  name:   str   =   "search_tool"  description:   str   =   ' 搜索互联网上公开内容的工具 '  return_direct:   bool   =   False  args_schema:   Type[BaseModel]   =   SearchArgs  def   _run(self,   query)   ->   str:  try:  print(" 执行我的   Python   中的工具，输入的参数为 :",   query)  response   =   zhipuai_client.web_search.web_search(  search_engine="search_pro",  search_query=query  )  #   print(response)  if   response.search_result:  return   "\n\n".join([d.content   for   d   in  response.search_result])  return   ' 没有搜索到任何内容！ '  except   Exception   as   e:  print(e)

## 第64页

return   ' 没有搜索到任何内容！ '  3 、 Agent   的上下文和记忆  一、上下文  小爱   AI   的注册地址： https://xiaoai.plus/register?aff=3TIp  上下文包括消息列表之外的  任何 数据，这些数据可以影响代理行为或工具执行。这可  以是：  •   运行时传入的信息，如   `user_id`   或   API   凭据。  •   多步推理过程中更新的内部状态。  •   来自先前交互的持久记忆或事实。  LangGraph   提供了 三种 提供上下文的主要方式：  点击图片可查看完整电子表格  您可以使用上下文来：  •   调整模型看到的系统提示  •   为工具提供必要的输入  •   在正在进行的对话中跟踪事实  Configurable

## 第65页

配置适用于不可变数据，如用户元数据或   API   密钥。当您有在运行期间不会更改的值  时使用。  使用保留用于此目的的键   "configurable"   指定配置。  C++  agent.invoke(  {"messages":   [{"role":   "user",   "content":   "hi!"}]},  config={"configurable":   {"user_id":   "user_123"}}  )  案例：通过   Configurable   中掺入参数，来动态设置系统提示词  状态   AgentState( 可变上下文 )  状态在运行期间充当   Agent   的记忆，可以短期存储也可以长期存储。它保存可在执行  期间演变的动态数据，例如从工具或   LLM   输出派生的值。  1 、搞清楚   AgentState   的作用。  2 、案例：（给用户发出一个祝福语句）输入   username   --->   config---->   工具   1--->   把  username   修改到   State   中 ------>   工具   2-----> 获取   State   的   username   得到最终答案。  二、记忆存储  这是一个强大的功能，允许您在多次调用中持久化代理的状态。否则，状态仅限于单  次运行。

## 第66页

短期存储：线程级存储（会话级）  短期存储使   Agent   能够跟踪多轮对话。要使用它，您必须：  1.   在创建代理时提供   checkpointer 。 checkpointer   可以实现代理状态的持久  性。  2.   在运行代理时在配置中提供   thread_id 。 thread_id   是对话会话的唯一标识符。  Python  #   内存：   开发环境  checkpointer   =   InMemorySaver()  #   在生产环境中，使用由数据库支持的检查点  DB_URI   =  "postgresql://postgres:postgres@localhost:5432/postgres?sslmode=di  sable"  with   PostgresSaver.from_conn_string(DB_URI)   as   checkpointer:  #   必须安装： pip   install   -U   "psycopg[binary,pool]"   langgraph-  checkpoint-postgres  #   生产环境： Redis  #   pip   install   -U   langgraph-checkpoint-redis  DB_URI   =   "redis://:6379"  with   RedisSaver.from_conn_string(DB_URI)   as   checkpointer:  长期存储：跨线程存储  使用长期内存来跨会话存储用户特定或应用程序特定的数据。这对于聊天机器人等应

## 第67页

用程序非常有用，您可能希望记住用户偏好或其他信息。  要使用长期内存，您需要：  1.   配置一个存储以在调用之间持久化数据。  2.   使用   get_store   函数从工具或提示中访问存储。  Python  #   开发环境中：   内存  store   =   InMemoryStore()  #   在生产环境中，使用由数据库支持的存储  DB_URI   =  "postgresql://postgres:postgres@localhost:5442/postgres?sslmode=di  sable"  with   (  PostgresStore.from_conn_string(DB_URI)   as   store,  PostgresSaver.from_conn_string(DB_URI)   as   checkpointer,  ):  #   store.setup()  #   checkpointer.setup()  DB_URI   =   "redis://:6379"  with   (  RedisStore.from_conn_string(DB_URI)   as   store,  RedisSaver.from_conn_string(DB_URI)   as   checkpointer,  ):  store.setup()  checkpointer.setup()  注意：  •   首次使用   Postgres   存储时，您需要调用   store.setup() ， checkpointer.setup()  •   首次使用   Redis   存储时，您需要调用   store.setup() ， checkpointer.setup()  •  第四章、 Agent   和   MCP   开发

## 第68页

1 、 Function   Calling （函数调用）  Function   Calling   由   OpenAI   等公司推动，允许大语言模型与外部工具连接，将自然  语言转换为   API   调用。这解决了大模型在训练结束，就知识更新停滞的问题。  通过调用外部工具和服务， Function   Calling   帮助大模型解决了比如今天温度多少度，  今天的大盘收盘点数是多少之类的实时性问题。  Function   Calling   的工作原理可以通过以下几个简单步骤来理解：  以天气查询为例， Function   Calling   的工作流程大致如下：  第一步，识别需求   ：这是一个关于实时天气的问题，需要调用外部天气   API 。  第二步，选择函数   ：从可用函数中选择   get_current_weather   函数。  第三步，准备参数   ：  Plain   Text

## 第69页

{  "location":   " 北京 ",  "unit":   "celsius"  }  第四步，调用函数   ：系统使用这些参数调用实际的天气   API ，获取北京的实时天气数  据。  第五步，整合回答   ：   " 根据最新数据，北京今天的天气晴朗，当前温度   23 ° C ，湿 度  45% ，微风。今天的最高温度预计为   26 ° C ，最低温度为   18 ° C 。 "  对开发者来说，使用   LLM   的   Function   Calling   起步相对容易，只需按照   API   要求定义  函数规格（通常   JSON   模式）并将其随请求发送，模型就可能按照需要调用这些函  数，逻辑较直观。  因此，对于 ** 单一模型、少量功能 ** 的简单应用， Function   Calling   实现起来非常直  接，几乎 “ 一键 ” 将模型输出对接到代码逻辑中。  然而，它的 ** 局限 ** 在于缺乏跨模型的一致性：每个   LLM   供应商的接口格式略有差  异，开发者若想支持多个模型，需要为不同   API   做适配或使用额外框架处理。而且，  ** 无状态性 **   ：模型仅生成调用规范，实际执行由外部系统完成。  2 、 MCP   协议和开发  1 、定义  MCP （ Model   Context   Protocol ，模型上下文协议）   ， 2024   年   11   月底，由   Anthropic  推出的一种开放标准，旨在统一大型语言模型（ LLM ）与外部数据源和工具之间的通  信协议。 MCP   的主要目的在于解决当前   AI   模型因数据孤岛限制而无法充分发挥潜力  的难题， MCP   使得   AI   应用能够安全地访问和操作本地及远程数据，为   AI   应用提供了  连接万物的接口。  Function   Calling   是   AI   模型调用函数的机制， MCP   是一个标准协议，使   AI   模型 与  API   无缝交互，而   AI   Agent   是一个自主运行的智能系统，利用   Function   Calling   和  MCP   来分析和执行任务，实现特定目标。

## 第70页

即使是最强大模型也会受到数据隔离的限制，形成信息孤岛，要做出更强大的模型，  每个新数据源都需要自己重新定制实现，使真正互联的系统难以扩展，存在很多的局  限性。  现在， MCP   可以直接在   AI   与数据（包括本地数据和互联网数据）之间架起一座桥  梁，通过   MCP   服务器和   MCP   客户端，大家只要都遵循这套协议，就能实现 “ 万物互  联 ” 。  有了   MCP ，可以和数据和文件系统、开发工具、 Web   和浏览器自动化、生产力和通  信、各种社区生态能力全部集成，实现强大的协作工作能力，它的价值远不可估量。  2 、 MCP   与   Function   Calling   的区别  •   MCP （ Model   Context   Protocol ），模型上下文协议  •   Function   Calling ，函数调用  这两种技术都旨在增强   AI   模型与外部数据的交互能力，但   MCP   不止可以增强   AI   模  型，还可以是其他的应用系统。

## 第71页

3 、工作原理  MCP   协议采用了一种独特的架构设计，它将   LLM   与资源之间的通信划分为三个主要  部分：客户端、服务器和资源。  客户端负责发送请求给   MCP   服务器，服务器则将这些请求转发给相应的资源。这种  分层的设计使得   MCP   协议能够更好地控制访问权限，确保只有经过授权的用户才能  访问特定的资源。  以下是   MCP   的基本工作流程：  •   初始化连接：客户端向服务器发送连接请求，建立通信通道。  •   发送请求：客户端根据需求构建请求消息，并发送给服务器。  •   处理请求：服务器接收到请求后，解析请求内容，执行相应的操作（如查询数据  库、读取文件等）。  •   返回结果：服务器将处理结果封装成响应消息，发送回客户端。  •   断开连接：任务完成后，客户端可以主动关闭连接或等待服务器超时关闭。

## 第72页

4 、通信机制  MCP   协议支持三种主要的通信机制：  •   1 、基于标准输入输出的本地通信（ stdio ）；  •   2 、基于   SSE （ Server-Sent   Events ）的远程通信。是一种基于   HTTP   协议的单  向通信协议，允许服务器以事件流的形式实时向客户端推送数据，而无需客户端明确  请求。 MCP   中的   SSE   Transport   结合了   SSE   技术和   HTTP   POST

## 第73页

•   3 、 Streamable-http  streamable   HTTP   是   MCP   协议在   2025   年   3   月引入的一种新传输机制，旨在取代  之前的   HTTP+SSE   传输模式。它的设计理念是在保留   SSE   优点的同时克服其限  制，特别是提供更好的可扩展性和企业环境兼容性。  Streamable   HTTP   的核心思想是提供一个统一的   HTTP   端点，同时支持   POST   和  GET   方法：  a.   POST   方法：用于客户端向服务器发送请求和接收响应  b.   GET   方法（可选）：用于建立   SSE   流，接收服务器实时推送的消息  与传统   HTTP+SSE   不同， Streamable   HTTP   不要求维护单独的初始化连接和消  息端点，简化了协议设计并提高了可靠性。

## 第74页

1.   连接 ：在   streamable   HTTP   模式下，并没有和   SSE   模式类似的 “ 连接 ” 过程（ 在  sse_client   调用时），因为无需事先创建   SSE   连接；  2.   客户端发起初始化请求（ Initialize ） 。如果是有状态模式，会在返回消息 的  HTTP   头中携带   session-id ；  3.   客户端发起初始化确认（ Initialized ） 。此时如果已有   session-id （有状态），客  户端会首先发起一次   HTTP   Get   请求，以建立独立的   SSE   通道；  4.   后续正常交互 ：普通的交互都是通过   Post   通道来进行，只有两种情况会使 用  SSE   通道：服务端发起的通知与请求、以及会话恢复的事件发送。  Streamable   HTTP   相比   SSE   的五大优势  1.   简化的通信模型  传统的   HTTP+SSE   方法需要两个不同的端点：一个用于建立连接，另一个用于发送消  息。而   Streamable   HTTP   提供了一个统一的端点，简化了客户端和服务器之间的交  互。  2.   支持无状态模式  Streamable   HTTP   的一个重要创新是支持完全无状态操作。通过设 置

## 第75页

sessionIdGenerator:   ()   =>   undefined ，服务器可以在不维护会话状态的情况下  处理请求，非常适合无服务器环境。比如：部署在   AWS   Lambda 、 Azure   Function s  等无服务器环境。短暂交互而非长期连接的场景。  3.   更好的可伸缩性  由于   Streamable   HTTP   可以在无状态模式下运行，它非常适合容器化和自动扩展场  景。服务器不需要维护长期连接，可以根据请求动态分配资源，显著提高可伸缩性。  这解决了   SSE   的一个主要问题：当有大量客户端时，每个客户端都需要维持一个长连  接，可能导致服务器资源耗尽。使用   Streamable   HTTP   的无状态模式，服务器只在处  理请求时分配资源，处理完成后即可释放。  4.   提高的可靠性  Streamable   HTTP   的简化设计减少了出错机会：  •   会话管理：在有状态模式下，会话   ID   通过   HTTP   头而非查询参数传递，减少安  全风险  •   重连处理：客户端可以在会话有效期内随时重连，无需复杂的重连逻辑  •   错误恢复：简化的协议使错误处理和恢复更加直观  5.   更好的企业环境兼容性  在企业环境中，代理服务器和防火墙常常会阻止非标准   HTTP   连接。 Streamable  HTTP   使用标准   HTTP   通信，大大减少了这类问题：  •   使用标准   HTTP   POST   和   GET ，无需特殊配置  •   不依赖长连接，减少代理超时问题  •   会话   ID   通过   HTTP   头传递，更符合企业安全要求  5 、 FastMCP ：构建模型上下文协议（ MCP ）服务器的快 速  Python   方案

## 第76页

Python  pip   install   langchain-mcp-adapters  Java   开发   MCP   服务： 把   SpringBoot   项目改造成   MCP   Server   非常简单   -   知乎  Python   开发   MCP   服务： FastMCP  开源的   MCP   服务项目： MCP   servers   |   Glama  它提供了一种简单且高效的方法来构建   MCP   服务器，为开发者提供强大的工具和资  源，从而帮助他们为   LLMs   提供上下文信息。  FastMCP   的主要特性：  •   快速：高层接口意味着更少的代码和更快的开发速度。  •   简单：构建   MCP   服务器时，所需的样板代码最少。  •   Pythonic ：符合   Python   开发者的直觉，使用起来更自然。  •   完整：致力于提供   MCP   规格的全面实现（当前某些高级功能仍在开发中）。 ♂  •   FastMCP   正在积极开发中，而   MCP   规格本身也在不断完善。  6 、 MCP   的认证和安全  FastMCP   的   Bearer   Token   Authentication   认证机制基于   JWT   (JSON   Web   Token)   标

## 第77页

准实现，是一种无状态的、基于声明的安全验证体系。  认证验证流程  当请求到达服务端时，按以下顺序验证：  •   存在性检查 ​   ：确认请求头包含   Authorization:   Bearer   <token>  •   结构验证 ​   ：检查   JWT   格式是否符合规范  •   签名验证 ​   ：使用配置的公钥验证签名有效性  •   声明校验 ​   ：  ￮   iss   必须匹配   BearerAuthProvider   配置的签发方  ￮   aud   必须包含服务端指定的受众  ￮   exp   必须未过期  •   权限检查 ​   ： Token   中的   scopes   需满足工具要求的权限  1.   生成   RSA   密钥对  作用 ​   ：生成用于   JWT   签名和验证的   RSA   密钥对  详细说明 ​   ：  •   生成一对   RSA   密钥（公钥和私钥）  •   公钥 ( public_key ) 用于验证   Token   签名  •   私钥 ( private_key ) 用于签发   Token  Python  #   1.   生成   RSA   密钥对（生产环境应从安全存储读取）  key_pair   =   RSAKeyPair.generate()  2.   配置   Bearer   认证提供方  Python  #   2.   配置认证提供方  auth   =   BearerAuthProvider(  public_key=key_pair.public_key,   #   公钥用于校验签名  issuer="http://localhost",   #   令牌签发方标识  audience="my-dev-server",   #   目标服务标识  )

## 第78页

3.   生成   token  Python  #   服务器，模拟生成一个   token  #   Generate   a   token   for   testing  token   =   key_pair.create_token(  subject="dev-user",  issuer="http://localhost",  audience="my-dev-server",  scopes=["read",   "write"]   #   token   中包含的数据  expires_in_seconds=3600   #   1   小时后过期  )  4.   客户端   Agent   传入   token  5.   服务器验证和获取   Token  get_access_token()  ￮   作用 ​   ：从当前请求中提取并解码   JWT  ￮   返回 ​   ： AccessToken   对象，包含以下主要属性：  Python  class   AccessToken:  client_id:   str   #   对应   JWT   的 'sub'(subject) 声明

## 第79页

scopes:   List[str]   #   对应   JWT   的 'scopes' 声明  issuer:   str   #   对应   JWT   的 'iss' 声明  token:   str   #   对应   JWT   的   Token   字符串  expires_at:   int   #   对应   JWT   的 'exp' 声明  第五章、基于   LangGraph   的   WorkFlow