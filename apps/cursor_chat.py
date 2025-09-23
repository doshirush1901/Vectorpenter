#!/usr/bin/env python3
"""
Cursor Chat REPL for Vectorpenter
Interactive chat interface optimized for use within Cursor IDE
"""

from __future__ import annotations
import sys
from typing import Dict, List
from pathlib import Path

from core.logging import logger
from index.embedder import embed_texts
from rag.retriever import vector_search
from rag.context_builder import hydrate_matches, build_context
from rag.generator import answer
from rag.reranker import rerank, is_rerank_available
from search.hybrid import hybrid_search, is_available as typesense_available

# Default settings for Cursor Chat
DEFAULT_K = 12
USE_HYBRID = True
USE_RERANK = True

class CursorChat:
    """Interactive chat interface for Vectorpenter"""
    
    def __init__(self):
        self.use_hybrid = USE_HYBRID and typesense_available()
        self.use_rerank = USE_RERANK and is_rerank_available()
        self.k = DEFAULT_K
        
    def print_welcome(self):
        """Print welcome message with configuration"""
        print("\n" + "="*60)
        print("🔨 VECTORPENTER CURSOR CHAT")
        print("The carpenter of context — building vectors into memory")
        print("="*60)
        print(f"Configuration:")
        print(f"  • Hybrid Search: {'✅ ON' if self.use_hybrid else '❌ OFF (Typesense unavailable)'}")
        print(f"  • Reranking: {'✅ ON' if self.use_rerank else '❌ OFF (No API keys)'}")
        print(f"  • Results (k): {self.k}")
        print("\nCommands:")
        print("  /help     - Show this help")
        print("  /config   - Show/change configuration")
        print("  /quit     - Exit chat")
        print("  /q        - Exit chat")
        print("\nType your questions and get grounded answers with citations!")
        print("-"*60)
    
    def print_help(self):
        """Print help information"""
        print("\n📖 HELP")
        print("Ask questions about your indexed documents.")
        print("Answers will include citations like [#1], [#2] referring to source chunks.")
        print("\nCommands:")
        print("  /help     - Show this help")
        print("  /config   - Show/change configuration") 
        print("  /quit, /q - Exit chat")
        print("  /sources  - Show sources for last answer")
        print("\nExamples:")
        print('  "What are the main features of the product?"')
        print('  "Summarize the Q3 financial results"')
        print('  "What did the CEO say about growth plans?"')
    
    def print_config(self):
        """Print current configuration"""
        print(f"\n⚙️  CONFIGURATION")
        print(f"  Hybrid Search: {'✅ ON' if self.use_hybrid else '❌ OFF'}")
        print(f"  Reranking: {'✅ ON' if self.use_rerank else '❌ OFF'}")
        print(f"  Results (k): {self.k}")
        print(f"  Typesense Available: {'✅' if typesense_available() else '❌'}")
        print(f"  Rerank Available: {'✅' if is_rerank_available() else '❌'}")
    
    def query(self, question: str) -> tuple[str, List[Dict]]:
        """Process a query and return answer with sources"""
        try:
            # Embed the query
            query_vec = embed_texts([question])[0]
            
            # Search for relevant chunks
            if self.use_hybrid:
                matches = hybrid_search(question, query_vec, k=self.k)
                search_type = "hybrid"
            else:
                matches = vector_search(query_vec, top_k=self.k)
                search_type = "vector"
            
            # Hydrate matches with full text
            snippets = hydrate_matches(matches)
            
            # Optional reranking
            if self.use_rerank and snippets:
                snippets = rerank(question, snippets)
                search_type += "+rerank"
            
            # Build context pack
            context_pack = build_context(snippets)
            
            # Generate answer
            if context_pack.strip():
                ans = answer(question, context_pack)
                logger.info(f"Query processed ({search_type}): {len(snippets)} sources")
            else:
                ans = "I don't have enough context to answer this question. Please make sure you have ingested and indexed some documents first."
                snippets = []
            
            return ans, snippets
            
        except Exception as e:
            logger.error(f"Query failed: {e}")
            return f"Sorry, I encountered an error: {e}", []
    
    def format_sources(self, snippets: List[Dict]) -> str:
        """Format sources list for display"""
        if not snippets:
            return "No sources found."
        
        sources = []
        for i, snippet in enumerate(snippets, 1):
            doc_name = snippet.get('doc', 'Unknown')
            seq = snippet.get('seq', 0)
            score = snippet.get('score', 0)
            rerank_score = snippet.get('rerank_score')
            source_type = snippet.get('source', 'unknown')
            
            score_info = f"score: {score:.3f}"
            if rerank_score is not None:
                score_info += f", rerank: {rerank_score:.3f}"
            
            sources.append(f"[#{i}] {doc_name}::{seq} ({source_type}, {score_info})")
        
        return "\n".join(sources)
    
    def run(self):
        """Run the interactive chat loop"""
        self.print_welcome()
        
        last_snippets = []
        
        try:
            while True:
                try:
                    # Get user input
                    user_input = input("\n🤖 Ask me anything: ").strip()
                    
                    if not user_input:
                        continue
                    
                    # Handle commands
                    if user_input.lower() in ['/quit', '/q']:
                        print("\n👋 Goodbye! Happy coding with Cursor!")
                        break
                    elif user_input.lower() == '/help':
                        self.print_help()
                        continue
                    elif user_input.lower() == '/config':
                        self.print_config()
                        continue
                    elif user_input.lower() == '/sources':
                        print(f"\n📚 SOURCES FROM LAST QUERY:")
                        print(self.format_sources(last_snippets))
                        continue
                    
                    # Process the query
                    print("\n🔍 Searching...")
                    ans, snippets = self.query(user_input)
                    last_snippets = snippets
                    
                    # Display the answer
                    print("\n" + "="*60)
                    print("📖 ANSWER:")
                    print("="*60)
                    print(ans)
                    
                    # Show sources summary
                    if snippets:
                        print(f"\n📚 Sources: {len(snippets)} chunks")
                        print("(Type '/sources' to see detailed source list)")
                    
                    print("-"*60)
                    
                except KeyboardInterrupt:
                    print("\n\n👋 Goodbye! Happy coding with Cursor!")
                    break
                except EOFError:
                    print("\n\n👋 Goodbye! Happy coding with Cursor!")
                    break
                    
        except Exception as e:
            logger.error(f"Chat loop error: {e}")
            print(f"\n❌ Fatal error: {e}")
            sys.exit(1)

def main():
    """Main entry point for Cursor Chat"""
    try:
        chat = CursorChat()
        chat.run()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye! Happy coding with Cursor!")
    except Exception as e:
        logger.error(f"Cursor Chat startup failed: {e}")
        print(f"❌ Failed to start Cursor Chat: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
