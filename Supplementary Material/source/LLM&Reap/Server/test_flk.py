from flashinfer import prefill

print("🛠️ Start JIT compiling FlashInfer module...")

module = prefill.get_batch_prefill_module(
    backend="cuda",
    q_dtype="bf16",
    kv_dtype="bf16",
    o_dtype="bf16",
    idx_dtype="i32",
    head_dim_qk=128,
    head_dim_vo=128,
    posenc=0,
    use_swa=False,
    use_logits_cap=False,
    f16qk=False
)

print("✅ FlashInfer JIT compile finished.")