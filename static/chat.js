document.addEventListener("DOMContentLoaded", function () {
    const chatHistoryDiv = document.getElementById("chat-history");
    const actionButton = document.getElementById("action-btn");
    const roundsInput = document.getElementById("rounds-input");
    const worldSettingInput = document.getElementById("world-setting");
    const updateWorldBtn = document.getElementById("update-world-btn");

    // 全局配置以config為準
    const config = {
        model: "",
        historyLength: 0, 
        temperature: 0,
        defaultRounds: 0 
    };

    // 角色模型配置
    const roleModels = {
        ai_left: "",
        ai_right: ""
    };

    // 初始化时获取服务器配置
    fetch("/get_config")
        .then(response => response.json())
        .then(data => {
            if (data.default_model) {
                config.model = data.default_model;
                console.log("已从服务器获取默认模型设置:", config.model);
            }
            if (data.chat_config) {
                config.historyLength = data.chat_config.history_length || config.historyLength;
                config.temperature = data.chat_config.temperature || config.temperature;
                config.defaultRounds = data.chat_config.default_rounds || config.defaultRounds;
                console.log("已从服务器获取对话配置:", data.chat_config);
                
                // 更新UI
                roundsInput.value = config.defaultRounds;
            }
            if (data.role_models) {
                Object.assign(roleModels, data.role_models);
                console.log("已从服务器获取角色模型设置:", roleModels);
            }
        })
        .catch(error => console.error("获取服务器配置失败:", error));

    // 狀態變數
    let conversationHistory = [];
    let round = 0;
    let maxRounds = config.defaultRounds;
    let currentWorldSetting = "";
    let lastSpeaker = ""; // 記錄最後一個說話者
    let lastChunk = ""; // 用於去重
    let isPaused = false; // 新增：用於追踪是否暫停

    // 更新世界設定按鈕事件
    updateWorldBtn.addEventListener("click", function () {
        if (actionButton.textContent === "正在對話...") return;
        updateWorldBtn.textContent = "以更新!!!";
        updateWorldBtn.disabled = true;
        currentWorldSetting = worldSettingInput.value.trim();
    });

    // 開始/繼續/暫停對話按鈕事件
    actionButton.addEventListener("click", function () {
        resetWorldButton();
        if (actionButton.textContent === "開始 AI 互動") {
            initializeNewDialog();
        } else if (actionButton.textContent === "繼續對話") {
            continueDialog();
        } else if (actionButton.textContent === "暫停對話") {
            pauseDialog();
        }
    });

    // 更新全局設定
    function updateGlobalSettings() {
        maxRounds = parseInt(roundsInput.value) || config.defaultRounds;
        currentWorldSetting = worldSettingInput.value.trim();
    }

    // 設置按鈕狀態
    function setActionButtonState(text, disabled) {
        if (text === "正在對話...") {
            actionButton.textContent = "暫停對話";
            actionButton.disabled = false;
        } else {
            actionButton.textContent = text;
            actionButton.disabled = disabled;
        }
    }

    // 初始化新對話
    function initializeNewDialog() {
        updateGlobalSettings();
        round = 0;
        conversationHistory = [];
        lastSpeaker = "";
        isPaused = false;
        setActionButtonState("正在對話...", true);
        aiTalk(roleModels.ai_left, "ai_left");
    }

    // 繼續對話
    function continueDialog() {
        updateGlobalSettings();
        round = 0;
        isPaused = false;
        setActionButtonState("正在對話...", true);
        let nextRole = lastSpeaker === "ai_left" ? "ai_right" : "ai_left";
        aiTalk(roleModels[nextRole], nextRole);
    }

    // 暫停對話
    function pauseDialog() {
        isPaused = true;
        setActionButtonState("繼續對話", false);
        resetWorldButton();
    }

    // 重置世界設定按鈕
    function resetWorldButton() {
        updateWorldBtn.textContent = "更新世界";
        updateWorldBtn.disabled = false;
    }

    // 發送聊天請求
    function sendChatRequest(model, role, history, message) {
        return fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                history: history.slice(-config.historyLength),
                message: message,
                temperature: config.temperature,
                model: model,
                role: role,
                world_setting: currentWorldSetting
            })
        });
    }

    // AI 對話邏輯
    function aiTalk(model, role) {
        updateGlobalSettings();

        const loadingBubble = appendMessage(role, "thinking...");
        let dots = 0;
        const loadingInterval = setInterval(() => {
            dots = (dots + 1) % 4;
            loadingBubble.textContent = `thinking${".".repeat(dots)}`;
        }, 500);

        let messageToSend = "";
        if (conversationHistory.length === 0) {
            messageToSend = "說說話";
        } else {
            for (let i = conversationHistory.length - 1; i >= 0; i--) {
                if (conversationHistory[i].role !== role) {
                    messageToSend = conversationHistory[i].content;
                    break;
                }
            }
            if (!messageToSend) {
                messageToSend = "對方沒有發言，請開始";
            }
        }

        sendChatRequest(model, role, conversationHistory, messageToSend)
            .then(response => {
                clearInterval(loadingInterval);
                loadingBubble.textContent = "";
                if (!response.ok) {
                    loadingBubble.textContent = `${model} 回應錯誤 (狀態碼: ${response.status})`;
                    return response.text().then(text => console.error("錯誤詳情:", text));
                }
                
                const reader = response.body.getReader();
                let fullText = "";
                function readChunk() {
                    reader.read().then(({ value, done }) => {
                        if (done) {
                            handleDialogEnd(role, fullText);
                            return;
                        }
                        const chunk = new TextDecoder().decode(value, { stream: true });
                        const processedChunk = chunk.replace(/data:/g, "").replace(/\n/g, "").replace(/\s+/g, " ").replace("[DONE]", "").trim();
                        fullText += processedChunk;
                        processStreamData(value);
                        readChunk();
                    });
                }
                readChunk();
            })
            .catch(handleFetchError);
    }

    // 處理對話結束
    function handleDialogEnd(role, fullText) {
        // 确保保存到历史记录的文本没有换行符和多余的空格
        const processedText = fullText.replace(/\n/g, " ").replace(/\s+/g, " ").trim();
        conversationHistory.push({ role: role, content: processedText });
        lastSpeaker = role;
        round++;

        if (isPaused) {
            return;
        }

        if (round >= maxRounds) {
            setActionButtonState("繼續對話", false);
            resetWorldButton();
        } else {
            const otherRole = role === "ai_left" ? "ai_right" : "ai_left";
            aiTalk(roleModels[otherRole], otherRole);
        }
    }

    // 處理流式數據
    function processStreamData(value) {
        const decoder = new TextDecoder("utf-8");
        const chunkValue = decoder.decode(value, { stream: true });
        const lines = chunkValue.split("\n\n");
        const loadingBubble = chatHistoryDiv.lastElementChild.querySelector(".bubble");

        for (const line of lines) {
            if (line.startsWith("data:")) {
                // 替换所有换行符为空格，移除所有 data: 前缀，并将多个连续空格替换为单个空格
                const data = line.replace(/data:/g, "").replace(/\n/g, " ").replace(/\s+/g, " ").trim();
                if (data !== "[DONE]" && data !== lastChunk) { // 避免重複
                    loadingBubble.textContent += data;
                    lastChunk = data;
                }
            }
        }
    }

    // 處理錯誤
    function handleFetchError(error) {
        clearInterval(loadingInterval);
        const loadingBubble = chatHistoryDiv.lastElementChild.querySelector(".bubble");
        loadingBubble.textContent = "錯誤：" + error.message;
        console.error("Fetch 錯誤:", error);
    }

    // 添加訊息到聊天歷史
    function appendMessage(role, text) {
        const msgDiv = document.createElement("div");
        msgDiv.className = `message ${role}`;
        msgDiv.innerHTML = `
            ${role === "ai_left" ? `
                <div class="avatar"><img src="/static/pic/left.jpg" alt="Avatar"></div>
                <div class="bubble">${text}</div>
            ` : `
                <div class="bubble">${text}</div>
                <div class="avatar"><img src="/static/pic/right.jpg" alt="Avatar"></div>
            `}
        `;
        chatHistoryDiv.appendChild(msgDiv);
        chatHistoryDiv.scrollTop = chatHistoryDiv.scrollHeight;
        return msgDiv.querySelector(".bubble");
    }
});