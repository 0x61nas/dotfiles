;;; $DOOMDIR/config.el -*- lexical-binding: t; -*-

;; Place your private configuration here! Remember, you do not need to run 'doom
;; sync' after modifying this file!


;; Some functionality uses this to identify you, e.g. GPG configuration, email
;; clients, file templates and snippets. It is optional.
(setq user-full-name "Anas Elgarhy"
      user-mail-address "anas.elgarhy.dev@gmail.com")



 ;; There are two ways to load a theme. Both assume the theme is installed and
 ;; available. You can either set `doom-theme' or manually load a theme with the
 ;; `Load-theme' function. This is the default:
                                        ;doom-theme 'doom-xcode
                                        ;doom-theme 'doom-one
                                        ;doom-theme 'consult-theme
                                        ;doom-theme 'doom-henna
(setq doom-theme 'doom-dracula)


 ;; doom exposes five (optional) variables for controlling fonts in doom:
 ;;
 ;; - `doom-font' -- the primary font to use
 ;; - `doom-variable-pitch-font' -- a non-monospace font (where applicable)
 ;; - `doom-big-font' -- used for `doom-big-font-mode'; use this for
 ;;   presentations or streaming.
 ;; - `doom-unicode-font' -- for unicode glyphs
 ;; - `doom-serif-font' -- for the `fixed-pitch-serif' face
 ;;
 ;; see 'c-h v doom-font' for documentation and more examples of what they
 ;; accept. for example:
 ;;
 ;; (setq doom-font (font-spec :family "FiraCode Nerd Font" :size 12 :weight 'semi-light))

 ;; Defult directory
  (setq default-directory "~")

 ;; Maps
(map! :ne "M-/" #'comment-or-uncomment-region)
 ;; (map! :ne "SPC / r" #'deadgrep)
 ;; (map! :ne "SPC n b" #'org-brain-visualize)

;; This determines the style of line numbers in effect. If set to `nil', line
;; numbers are disabled. For relative line numbers, set this to `relative'.
(setq display-line-numbers-type 'relative)

;; If you use `org' and don't want your org files in the default location below,
;; change `org-directory'. It must be set before org loads!
(setq org-directory "~/org/")


;; Whenever you reconfigure a package, make sure to wrap your config in an
;; `after!' block, otherwise Doom's defaults may override your settings. E.g.
;;
;;   (after! PACKAGE
;;     (setq x y))
;;
;; The exceptions to this rule:
;;
;;   - Setting file/directory variables (like `org-directory')
;;   - Setting variables which explicitly tell you to set them before their
;;     package is loaded (see 'C-h v VARIABLE' to look up their documentation).
;;   - Setting doom variables (which start with 'doom-' or '+').
;;
;; Here are some additional functions/macros that will help you configure Doom.
;;
;; - `load!' for loading external *.el files relative to this one
;; - `use-package!' for configuring packages
;; - `after!' for running code after a package has loaded
;; - `add-load-path!' for adding directories to the `load-path', relative to
;;   this file. Emacs searches the `load-path' when you load packages with
;;   `require' or `use-package'.
;; - `map!' for binding new keys
;;
;; To get information about any of these functions/macros, move the cursor over
;; the highlighted symbol at press 'K' (non-evil users must press 'C-c c k').
;; This will open documentation for it, including demos of how they are used.
;; Alternatively, use `C-h o' to look up a symbol (functions, variables, faces,
;; etc).
;;
;; You can also try 'gd' (or 'C-c c d') to jump to their definition and see how
;; they are implemented.

;; accept completion from copilot and fallback to company
(use-package! copilot
  :hook (prog-mode . copilot-mode)
  :bind (("C-TAB" . 'copilot-accept-completion-by-word)
         ("C-<tab>" . 'copilot-accept-completion-by-word)
         :map copilot-completion-map
         ("<tab>" . 'copilot-accept-completion)
         ("TAB" . 'copilot-accept-completion)))

(global-wakatime-mode)
