//
//  ModelData.swift
//  PaperPilot
//
//  Created by 林思行 on 2023/9/24.
//

// swiftlint:disable line_length

import Foundation
import SwiftData

class ModelData {
    static var paper1 = Paper(title: "A Study of Machine Learning Techniques for Sentiment Analysis",
                              abstract: "In this paper, we explore various machine learning techniques for sentiment analysis, including support vector machines, decision trees, and neural networks.",
                              keywords: ["machine learning", "sentiment analysis", "support vector machines", "decision trees", "neural networks"],
                              authors: ["John Smith", "Jane Doe"],
                              tags: ["machine learning", "sentiment analysis"],
                              publicationYear: "2021",
                              publication: "Journal of Machine Learning Research",
                              volume: "42",
                              issue: "3",
                              pages: "123-135",
                              url: "https://www.jmlr.org/papers/v42/Smith21a.html",
                              doi: "10.5555/123456789",
                              file: try! Bundle.main.url(forResource: "frames", withExtension: "pdf")?.bookmarkData())
    static var paper2 = Paper(title: "An Introduction to Swift Programming",
                              abstract: nil,
                              keywords: [],
                              authors: ["John Smith"],
                              tags: ["Swift", "Programming"],
                              publicationYear: "2020",
                              publication: "ACM Transactions on Programming Languages and Systems",
                              volume: nil,
                              issue: nil)
    static var paper3 = Paper(title: "A Comprehensive Study of Natural Language Processing Techniques",
                              abstract: "In this paper, we present a comprehensive study of natural language processing techniques, including tokenization, part-of-speech tagging, named entity recognition, and sentiment analysis. We evaluate the performance of these techniques on several benchmark datasets and provide recommendations for future research.",
                              keywords: ["natural language processing", "tokenization", "part-of-speech tagging", "named entity recognition", "sentiment analysis"],
                              authors: ["John Smith", "Jane Doe", "Bob Johnson"],
                              tags: ["natural language processing", "machine learning", "sentiment analysis"],
                              publicationYear: "2022",
                              publication: "IEEE Transactions on Natural Language Processing",
                              volume: "10",
                              issue: "2",
                              file: try! Bundle.main.url(forResource: "frames", withExtension: "pdf")?.bookmarkData())
    static var project1 = Project(name: "Demo project", desc: "CVPR24 Project", papers: [paper1, paper2, paper3])
    static var project2 = Project(name: "test2", desc: "", papers: [paper2, paper3])
}

// swiftlint:enable line_length

@MainActor
let previewContainer: ModelContainer = {
    do {
        let container = try ModelContainer(for: Paper.self, Project.self,
                                           configurations: ModelConfiguration(isStoredInMemoryOnly: true))
        container.mainContext.insert(ModelData.project1)
        return container
    } catch {
        fatalError("Failed to create container")
    }
}()
