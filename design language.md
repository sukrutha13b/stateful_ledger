# **Gemini Design Language System (Dark Mode)**

## **1\. Core Design Principles**

* **Focus-Driven:** The interface melts away to prioritize the conversation and content.  
* **Fluid & Organic:** Utilizing generous rounded corners (pill shapes) and soft gradient glows to feel more human and less rigid.  
* **Progressive Disclosure:** Advanced features (sidebar history, model selection) are neatly tucked away or collapsed by default to prevent cognitive overload.

## **2\. Color Palette**

Gemini heavily utilizes a Material 3-inspired dark theme, relying on deeply desaturated cool grays to reduce eye strain, punctuated by the vibrant "Gemini Spark" gradient.

### **Backgrounds & Surfaces**

* **Base Background:** \#131314 (Deepest Charcoal/Black) – Used for the main canvas and empty states.  
* **Surface Container (Low):** \#1E1F20 (Dark Gray) – Used for the expanded sidebar and floating input bar.  
* **Surface Container (High):** \#282A2C (Medium Dark Gray) – Used for hover states, tooltips, and file attachment cards.

### **Typography & Icons**

* **Primary Text:** \#E2E2E2 (Off-White) – Used for user prompts, AI responses, and active UI elements.  
* **Secondary Text/Icons:** \#C4C7C5 (Light Gray) – Used for timestamps, placeholder text ("Ask Gemini"), and inactive icons.

### **Brand Accents & Effects**

* **Ambient Glow:** A very soft, low-opacity radial gradient centered behind the "Where should we start?" text, blending deep indigo and purple into the base background.  
* **Gemini Spark:** The four-point star logo uses a gradient combining Google's core colors (Blue, Red/Orange, Yellow, Green) adapted for dark mode visibility.  
* **User Avatar:** \#1E8E3E (Material Green) with white text for the user profile circle.

## **3\. Typography**

The interface relies on clean, highly legible sans-serif typography (Google Sans and standard system sans-serif fallbacks).

* **Display / Greeting:**  
  * *Usage:* "Where should we start?"  
  * *Style:* \~32px, Regular/Medium weight, Centered, High contrast.  
* **Body Text (Chat):**  
  * *Usage:* User prompts and Gemini responses.  
  * *Style:* \~16px, Regular weight, Left-aligned.  
  * *Line Height:* Generous (\~150% or 1.5) to ensure readability for long-form generated text.  
* **UI Labels & Metadata:**  
  * *Usage:* Sidebar history, button labels, model selector ("Pro Extended").  
  * *Style:* \~14px, Medium weight, Truncated with ellipses for long chat titles.

## **4\. Shape & Elevation**

The geometry of Gemini is distinctly round, avoiding sharp edges to create an approachable AI persona.

* **Pill Shapes (Fully Rounded \- e.g.,** border-radius: 50px**):**  
  * Main prompt input field.  
  * "New chat" button in the expanded sidebar.  
  * Dropdown selectors (e.g., the Model selector).  
* **Rounded Rectangles (Soft Corners \- e.g.,** border-radius: 12px **to** 16px**):**  
  * Attached file cards (like the Word and Code documents in Screenshot 1).  
  * Image attachment previews inside the input box.  
* **Elevation (Shadows):**  
  * Extremely minimal. The UI relies primarily on slight color step-ups (Base to Surface) rather than drop shadows to establish hierarchy.

## **5\. Key UI Components**

### **The Input Bar (The "Command Center")**

* **Structure:** A floating, pill-shaped container positioned at the bottom center.  
* **Anatomy:**  
  * *Left:* '+' (Plus) icon for attachments.  
  * *Center:* Text input field with "Ask Gemini" placeholder.  
  * *Right:* Model selector dropdown ("Pro Extended"), Microphone icon for voice input.  
* **Behavior:** Expands vertically as the user types multi-line prompts or attaches media (as seen in Screenshot 3 where images stack above the text line).

### **Navigation Sidebar**

* **States:** Collapsed (icons only) vs. Expanded (icons \+ text).  
* **Hierarchy:**  
  1. Primary Action ("New chat" pill button).  
  2. Global Links (Search chats, Videos, Library, Notebooks).  
  3. Recents (Chronological list of past chats with a "Notebooks" sub-header).  
  4. User Profile (Bottom pinned).

### **Chat Canvas (Response Area)**

* **User Prompt:** Right-aligned or center-aligned within a max-width container. Distinctly darker or uses a subtle surface background if separated from the main flow.  
* **AI Response:** Left-aligned, utilizing Markdown formatting (bolding, tables, bullet points) for clear information hierarchy.  
* **Action Row:** Small utility icons beneath the AI response (Copy, Edit/Regenerate) to manage the output.

