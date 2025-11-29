/**
 * TipTap extension for embedding Excalidraw drawings in notes.
 *
 * Usage in editor:
 * editor.chain().focus().insertExcalidrawBlock({ drawingId: '...' }).run()
 */

import { Node, mergeAttributes } from '@tiptap/core';
import { ReactNodeViewRenderer } from '@tiptap/react';
import { ExcalidrawBlockNode } from './ExcalidrawBlockNode';

export interface ExcalidrawBlockOptions {
  HTMLAttributes: Record<string, unknown>;
}

declare module '@tiptap/core' {
  interface Commands<ReturnType> {
    excalidrawBlock: {
      /**
       * Insert an Excalidraw drawing block
       */
      insertExcalidrawBlock: (attrs: {
        drawingId: string;
        editMode?: 'modal' | 'inline';
        width?: number;
        height?: number;
      }) => ReturnType;
    };
  }
}

export const ExcalidrawBlock = Node.create<ExcalidrawBlockOptions>({
  name: 'excalidrawBlock',

  group: 'block',

  atom: true, // Non-editable as a whole

  draggable: true,

  addOptions() {
    return {
      HTMLAttributes: {},
    };
  },

  addAttributes() {
    return {
      drawingId: {
        default: null,
        parseHTML: (element) => element.getAttribute('data-drawing-id'),
        renderHTML: (attributes) => ({
          'data-drawing-id': attributes.drawingId,
        }),
      },
      editMode: {
        default: 'modal',
        parseHTML: (element) => element.getAttribute('data-edit-mode') || 'modal',
        renderHTML: (attributes) => ({
          'data-edit-mode': attributes.editMode,
        }),
      },
      width: {
        default: 800,
        parseHTML: (element) => parseInt(element.getAttribute('data-width') || '800', 10),
        renderHTML: (attributes) => ({
          'data-width': attributes.width,
        }),
      },
      height: {
        default: 400,
        parseHTML: (element) => parseInt(element.getAttribute('data-height') || '400', 10),
        renderHTML: (attributes) => ({
          'data-height': attributes.height,
        }),
      },
    };
  },

  parseHTML() {
    return [
      {
        tag: 'div[data-excalidraw-block]',
      },
    ];
  },

  renderHTML({ HTMLAttributes }) {
    return [
      'div',
      mergeAttributes(this.options.HTMLAttributes, HTMLAttributes, {
        'data-excalidraw-block': '',
      }),
    ];
  },

  addNodeView() {
    return ReactNodeViewRenderer(ExcalidrawBlockNode);
  },

  addCommands() {
    return {
      insertExcalidrawBlock:
        (attrs) =>
        ({ commands }) => {
          return commands.insertContent({
            type: this.name,
            attrs,
          });
        },
    };
  },
});

export default ExcalidrawBlock;
