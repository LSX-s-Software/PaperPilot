//
//  AddPaperView.swift
//  PaperPilot
//
//  Created by 林思行 on 2023/10/10.
//

import SwiftUI

struct AddPaperView: View {
    @Environment(\.dismiss) private var dismiss
    
    @Bindable var project: Project
    @State private var newPaper = Paper(title: "")
    @State private var filePath: URL?
    @State private var isImporting = false
    @State private var shouldGoNext = false
    @State private var shouldClose = false
    
    var body: some View {
        NavigationStack {
            ImageTitleDialog(title: "Add Paper", systemImage: "doc.fill.badge.plus") {
                VStack {
                    NavigationLink {
                        AddPaperByURLView(project: project)
                    } label: {
                        HStack {
                            Image(systemName: "link")
                                .font(.system(size: 24))
                            VStack(alignment: .leading) {
                                Text("From URL/DOI")
                                    .font(.headline)
                                    .fontWeight(.medium)
                                Text("Add paper from a URL or DOI")
                                    .font(.subheadline)
                                    .foregroundStyle(.secondary)
                            }
                        }
                        .padding(10)
                        .frame(maxWidth: .infinity, alignment: .leading)
                    }
                    
                    Button {
                        isImporting = true
                    } label: {
                        HStack {
                            Image(systemName: "doc.badge.arrow.up")
                                .font(.system(size: 24))
                            VStack(alignment: .leading) {
                                Text("From file")
                                    .font(.headline)
                                    .fontWeight(.medium)
                                Text("Add paper from local file")
                                    .font(.subheadline)
                                    .foregroundStyle(.secondary)
                            }
                        }
                        .padding(10)
                        .frame(maxWidth: .infinity, alignment: .leading)
                    }
                    .fileImporter(
                        isPresented: $isImporting,
                        allowedContentTypes: [.pdf]
                    ) { result in
                        switch result {
                        case .success(let url):
                            filePath = url
                            newPaper.title = url.deletingPathExtension().lastPathComponent
                            newPaper.url = url.path
                            shouldGoNext = true
                        case .failure(let error):
                            print(error)
                        }
                    }
                }
                .fixedSize(horizontal: true, vertical: false)
            }
            .navigationDestination(isPresented: $shouldGoNext) {
                AddPaperByFileView(project: project, paper: newPaper, shouldClose: $shouldClose)
            }
        }
        .onChange(of: shouldClose) {
            if shouldClose {
                dismiss()
            }
        }
    }
}

#Preview {
    AddPaperView(project: ModelData.project1)
        .modelContainer(previewContainer)
}
